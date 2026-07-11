#!/usr/bin/env python3
"""ASP-Bench Tier 3: decrypt a submission archive for evaluation or review.

Usage: python tools/unpack.py problems/t3_001_name.zip [-o OUTDIR]

Extracts into OUTDIR (default: ./t3_001_name.plain/ — the *.plain pattern is
gitignored so decrypted material is not committed by accident) and prints the
plaintext fingerprint for comparison against INDEX.md.
"""

import argparse
import base64
import hashlib
import sys
from pathlib import Path

TOOLS_DIR = Path(__file__).resolve().parent
REQUIRED_FILES = ["metadata.yml", "problem.md", "ground_truth.py", "solution.py"]


def password() -> str:
    return base64.b64decode((TOOLS_DIR / "password.b64").read_text().strip()).decode()


def fingerprint(subdir: Path) -> str:
    h = hashlib.sha256()
    for name in REQUIRED_FILES:
        h.update(name.encode() + b"\0" + (subdir / name).read_bytes() + b"\0")
    return h.hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("archive", type=Path)
    p.add_argument("-o", "--outdir", type=Path, default=None)
    args = p.parse_args()

    import pyzipper
    outdir = args.outdir or Path(args.archive.stem + ".plain")
    outdir.mkdir(parents=True, exist_ok=True)
    with pyzipper.AESZipFile(args.archive) as zf:
        zf.setpassword(password().encode())
        zf.extractall(outdir)
    print(f"OK    extracted {args.archive.name} -> {outdir}/")
    print(f"OK    plaintext fingerprint sha256:{fingerprint(outdir)}")
    print("NOTE  decrypted files are for local use only — never commit or paste them")
    return 0


if __name__ == "__main__":
    sys.exit(main())
