#!/usr/bin/env python3
"""ASP-Bench Tier 3 submission tool.

Subcommands:
    verify DIR          run all format and validation checks on a submission directory
    pack DIR [-o OUT]   verify, then create the encrypted archive problems/t3_NNN_slug.zip
    canary              print the canary line that must appear in problem.md and ground_truth.py

The archive password and the canary string are stored base64-encoded so that
neither appears as plain text in the repository (contamination speed-bump, not
a secret). See README.md for the threat model.

Requires: Python >= 3.10, pyyaml, pyzipper (pack only), clingo==5.8.* (to run
the example solution). Install with: pip install -r tools/requirements.txt
"""

import argparse
import ast
import base64
import hashlib
import json
import subprocess
import sys
from pathlib import Path

TOOLS_DIR = Path(__file__).resolve().parent

CANARY_B64 = "QVNQLUJFTkNILVRJRVIzIENBTkFSWSA2ZDdmNGFjOS1iY2U2LTRiZGMtYjRiMS04NWNkODE5NmQ5MDc="

REQUIRED_FILES = ["metadata.yml", "problem.md", "ground_truth.py", "solution.py"]
ASPECTS = {"OPT", "TEMP", "DEFAULT", "RESOURCE", "RECURSIVE", "SPATIAL", "QUANT"}

MAX_WORDS = 1000          # problem.md word limit
MAX_BYTES = 12288         # problem.md byte limit (12 KB)
SOLUTION_TIMEOUT = 60     # seconds, end-to-end run of solution.py
GROUND_TRUTH_TIMEOUT = 10 # seconds, run of ground_truth.py


def canary() -> str:
    return base64.b64decode(CANARY_B64).decode()


def password() -> str:
    return base64.b64decode((TOOLS_DIR / "password.b64").read_text().strip()).decode()


def fingerprint(subdir: Path) -> str:
    """SHA-256 over the four plaintext files in fixed order."""
    h = hashlib.sha256()
    for name in REQUIRED_FILES:
        h.update(name.encode() + b"\0" + (subdir / name).read_bytes() + b"\0")
    return h.hexdigest()


def check_metadata(subdir: Path, errors: list) -> dict:
    import yaml
    try:
        meta = yaml.safe_load((subdir / "metadata.yml").read_text())
    except Exception as e:
        errors.append(f"metadata.yml: cannot parse YAML ({e})")
        return {}
    if not isinstance(meta, dict):
        errors.append("metadata.yml: top level must be a mapping")
        return {}

    number = meta.get("number")
    if not isinstance(number, int) or not (0 <= number <= 999):
        errors.append("metadata.yml: 'number' must be an integer 0-999 (0 is reserved for the template)")
    import re
    slug = meta.get("slug", "")
    if not isinstance(slug, str) or not re.fullmatch(r"[a-z][a-z0-9_]{0,23}", slug):
        errors.append("metadata.yml: 'slug' must be lowercase snake_case, "
                      "1-24 chars, starting with a letter ([a-z][a-z0-9_]{0,23})")
    if not isinstance(meta.get("title"), str) or not meta.get("title"):
        errors.append("metadata.yml: 'title' must be a non-empty string")
    authors = meta.get("authors")
    if not isinstance(authors, list) or not authors or not all(isinstance(a, str) for a in authors):
        errors.append("metadata.yml: 'authors' must be a non-empty list of names")
    if not isinstance(meta.get("contact"), str) or "@" not in meta.get("contact", ""):
        errors.append("metadata.yml: 'contact' must be an email address")
    aspects = meta.get("aspects")
    if not isinstance(aspects, list) or not aspects or not set(aspects) <= ASPECTS:
        errors.append(f"metadata.yml: 'aspects' must be a non-empty subset of {sorted(ASPECTS)}")
    if not isinstance(meta.get("optimization"), bool):
        errors.append("metadata.yml: 'optimization' must be true or false")
    if meta.get("optimization") and not isinstance(meta.get("optimal_value"), (int, float)):
        errors.append("metadata.yml: optimization problems must state the numeric 'optimal_value'")
    if not meta.get("optimization") and "optimal_value" in meta:
        errors.append("metadata.yml: 'optimal_value' given but 'optimization' is false")
    cv = meta.get("clingo_version", "")
    if not (isinstance(cv, str) and cv.startswith("5.8")):
        errors.append("metadata.yml: 'clingo_version' must be a 5.8.x version string")
    if meta.get("license") != "Apache-2.0":
        errors.append("metadata.yml: 'license' must be exactly 'Apache-2.0'")
    return meta


def check_problem_md(subdir: Path, errors: list):
    path = subdir / "problem.md"
    data = path.read_bytes()
    text = data.decode("utf-8", errors="replace")
    nwords = len(text.split())
    if nwords > MAX_WORDS:
        errors.append(f"problem.md: {nwords} words exceeds the {MAX_WORDS}-word limit "
                      "(instance data must be compact or rule-generated, not enumerated)")
    if len(data) > MAX_BYTES:
        errors.append(f"problem.md: {len(data)} bytes exceeds the {MAX_BYTES}-byte limit")
    if canary() not in text:
        errors.append("problem.md: missing canary line (run 'python tools/pack.py canary' and paste it at the end)")
    if "json" not in text.lower():
        errors.append("problem.md: must specify the required JSON output format")


def _stdlib_only(path: Path, errors: list, label: str):
    try:
        tree = ast.parse(path.read_text(), filename=str(path))
    except SyntaxError as e:
        errors.append(f"{label}: syntax error ({e})")
        return None
    for node in ast.walk(tree):
        mods = []
        if isinstance(node, ast.Import):
            mods = [a.name for a in node.names]
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            mods = [node.module]
        for m in mods:
            top = m.split(".")[0]
            if top not in sys.stdlib_module_names:
                errors.append(f"{label}: imports non-stdlib module '{top}' "
                              "(validators must be plain Python 3, standard library only)")
    return tree


def check_ground_truth(subdir: Path, meta: dict, errors: list):
    path = subdir / "ground_truth.py"
    tree = _stdlib_only(path, errors, "ground_truth.py")
    if canary() not in path.read_text():
        errors.append("ground_truth.py: missing canary comment (run 'python tools/pack.py canary')")
    if tree is None or not meta.get("optimization"):
        return
    # optimization problems must pin the known optimum as EXPECTED_OPTIMAL
    found = None
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for tgt in node.targets:
                if isinstance(tgt, ast.Name) and tgt.id == "EXPECTED_OPTIMAL":
                    try:
                        found = ast.literal_eval(node.value)
                    except ValueError:
                        pass
    if found is None:
        errors.append("ground_truth.py: optimization problems must define a module-level "
                      "constant EXPECTED_OPTIMAL with the known optimal value")
    elif found != meta.get("optimal_value"):
        errors.append(f"ground_truth.py: EXPECTED_OPTIMAL = {found!r} does not match "
                      f"metadata optimal_value = {meta.get('optimal_value')!r}")


def check_solution_runs(subdir: Path, errors: list):
    try:
        sol = subprocess.run([sys.executable, str(subdir / "solution.py")],
                             capture_output=True, text=True, timeout=SOLUTION_TIMEOUT,
                             cwd=subdir)
    except subprocess.TimeoutExpired:
        errors.append(f"solution.py: exceeded the {SOLUTION_TIMEOUT}s end-to-end limit")
        return
    if sol.returncode != 0:
        errors.append(f"solution.py: exited with code {sol.returncode} "
                      f"(stderr: {sol.stderr.strip()[:200]})")
        return
    try:
        gt = subprocess.run([sys.executable, str(subdir / "ground_truth.py")],
                            input=sol.stdout, capture_output=True, text=True,
                            timeout=GROUND_TRUTH_TIMEOUT, cwd=subdir)
    except subprocess.TimeoutExpired:
        errors.append(f"ground_truth.py: exceeded the {GROUND_TRUTH_TIMEOUT}s limit")
        return
    if gt.returncode != 0:
        errors.append(f"ground_truth.py: exited with code {gt.returncode} "
                      f"(stderr: {gt.stderr.strip()[:200]})")
        return
    try:
        verdict = json.loads(gt.stdout.strip().splitlines()[-1])
    except (json.JSONDecodeError, IndexError):
        errors.append("ground_truth.py: output is not a JSON object "
                      '(expected {"valid": true/false, "message": "..."})')
        return
    if verdict.get("valid") is not True:
        errors.append(f"validation failed: example solution rejected by ground truth "
                      f"(message: {str(verdict.get('message'))[:200]})")


def verify(subdir: Path) -> dict | None:
    """Run all checks; print pass/fail per check but never file contents."""
    errors: list = []
    missing = [f for f in REQUIRED_FILES if not (subdir / f).is_file()]
    if missing:
        print(f"FAIL  missing files: {', '.join(missing)}")
        return None
    meta = check_metadata(subdir, errors)
    check_problem_md(subdir, errors)
    check_ground_truth(subdir, meta, errors)
    try:
        ast.parse((subdir / "solution.py").read_text())
    except SyntaxError as e:
        errors.append(f"solution.py: syntax error ({e})")
    if not errors:
        check_solution_runs(subdir, errors)
    if errors:
        for e in errors:
            print(f"FAIL  {e}")
        return None
    print("OK    all checks passed")
    print(f"OK    plaintext fingerprint sha256:{fingerprint(subdir)}")
    return meta


def pack(subdir: Path, outdir: Path) -> int:
    meta = verify(subdir)
    if meta is None:
        return 1
    import pyzipper
    name = f"t3_{meta['number']:03d}_{meta['slug']}.zip"
    outdir.mkdir(parents=True, exist_ok=True)
    out = outdir / name
    with pyzipper.AESZipFile(out, "w", compression=pyzipper.ZIP_DEFLATED,
                             encryption=pyzipper.WZ_AES) as zf:
        zf.setpassword(password().encode())
        for fname in REQUIRED_FILES:
            zf.write(subdir / fname, fname)
    sha = fingerprint(subdir)
    aspects = ",".join(meta["aspects"])
    opt = "yes" if meta["optimization"] else "no"
    print(f"OK    wrote {out}")
    print("\nAdd this row to INDEX.md:")
    print(f"| {meta['number']:03d} | {meta['title']} | {', '.join(meta['authors'])} "
          f"| {aspects} | {opt} | `{sha[:16]}` | submitted |")
    return 0


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    v = sub.add_parser("verify", help="run all checks on a submission directory")
    v.add_argument("dir", type=Path)
    k = sub.add_parser("pack", help="verify and create the encrypted archive")
    k.add_argument("dir", type=Path)
    k.add_argument("-o", "--outdir", type=Path, default=Path("problems"))
    sub.add_parser("canary", help="print the canary line for problem.md and ground_truth.py")
    args = p.parse_args()

    if args.cmd == "canary":
        print(canary())
        return 0
    # Resolve to an absolute path: verify/pack run solution.py with
    # cwd set to the submission dir, so a relative dir would be looked
    # up twice (cwd/dir/solution.py) and fail to open.
    if args.cmd == "verify":
        return 0 if verify(args.dir.resolve()) is not None else 1
    return pack(args.dir.resolve(), args.outdir.resolve())


if __name__ == "__main__":
    sys.exit(main())
