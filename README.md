# ASP-Bench

ASP-Bench is a benchmark for evaluating LLM agents on translating
natural-language problem descriptions into Answer Set Programs (ASP).
See the paper *ASP-Bench: From Natural Language to Logic Programs*
([arXiv:2602.01171](https://arxiv.org/abs/2602.01171)), presented at NSE '26
and ICLP 2026.

| Tier | Content | Where | Status |
|---|---|---|---|
| 1 | 64 easy problems | [Zenodo](https://doi.org/10.5281/zenodo.18062939) (encrypted) | saturated |
| 2 | 64 hard problems | [Zenodo](https://doi.org/10.5281/zenodo.18062939) (encrypted) | saturated |
| 3 | community-contributed hard problems | this repository | **open call** |

Tiers 1 and 2 are **saturated**: a ReAct-style agent with solver feedback
solves all 128 problems (see the paper).

## Tier 3 — Call for Hard Problems

**Tier 3 is a community-contributed collection of problems that current
systems cannot solve reliably.** This repository accepts submissions by pull
request. Contributors are credited in [INDEX.md](INDEX.md), in the Zenodo
releases, and in any follow-up publication.

## What counts as a Tier-3 problem

- A **natural-language problem statement** (at most 1,000 words, self-contained)
  that is naturally modeled in ASP and solvable with clingo, with each solver
  call finishing within **20 seconds** on commodity hardware.
- **Unambiguous.** The statement must say precisely what constitutes a
  solution and exactly which JSON fields the output must contain and what
  they mean. Tier 3 tests whether a system can *model a clearly stated
  problem* in ASP/clingo — not whether it can guess the author's intent.
  Difficulty must come from the modeling, never from vagueness in the
  specification or the output format.
- A **ground truth validator**: a plain-Python script that semantically checks
  *any* proposed solution — not string comparison against one reference answer.
- An **example solution** using the clingo Python API, proving the problem is
  well-posed (for optimization problems: proving the stated optimum is attained).
- **Hard — measured, not asserted.** Accepted problems are **Tier-3
  candidates**. During review, the maintainer runs the Tier-3 **reference
  agent** — the ASP-Bench coder with the `clingo.md` project prompt (see the
  paper) running **`openai/gpt-5.6-sol`**
  (config: [`tools/models/gpt56sol.json`](tools/models/gpt56sol.json)) —
  **three times** on the problem, and publishes the record in
  [INDEX.md](INDEX.md): successes out of 3, execution calls, tokens, and
  time per run. For calibration: the reference agent solves the 10 hardest
  Tier-1/2 problems in 3–6 execution calls each, so a candidate should push
  it well beyond that envelope — reference-agent *failures* are the gold
  standard. Once enough candidates accumulate, the published records will
  show where the actual Tier-3 goalpost lies, and formal qualification
  criteria will be pinned then. You can run the same test yourself before
  submitting — see the optional hardness self-test in
  [SUBMISSION_GUIDE.md](SUBMISSION_GUIDE.md). (The paper's Claude Sonnet 4.5
  baseline is superseded for Tier-3 purposes; the reference model will be
  re-pinned as the frontier advances.)

See [SUBMISSION_GUIDE.md](SUBMISSION_GUIDE.md) for the complete specification.

## Why everything is encrypted

Problem statements and validators must stay out of LLM training data —
otherwise the benchmark silently stops measuring anything. Therefore
**plaintext never appears in this repository**: not in files, commits, pull
requests, issues, or CI logs. Submissions are AES-256-encrypted zip archives.

This is a *contamination speed-bump, not a secret*: the password is available
to every human evaluator (base64-encoded in [`tools/password.b64`](tools/password.b64);
the tools decode it automatically). Crawlers and training pipelines do not
decrypt archives; humans take ten seconds. Additionally, every plaintext file
carries a canary string (`python tools/pack.py canary`) so that future
contamination is detectable, following the BIG-bench practice.

## How to submit

1. Install the tooling (Python ≥ 3.10):
   `pip install -r tools/requirements.txt`
2. Copy the template into the gitignored working directory:
   `mkdir -p work && cp -r template work/my_problem`
3. Write `problem.md`, `ground_truth.py`, `solution.py`, and `metadata.yml`
   (pick the next free number from [INDEX.md](INDEX.md)). Insert the canary
   line printed by `python tools/pack.py canary` where the templates indicate.
4. Validate and encrypt:
   `python tools/pack.py pack work/my_problem`
   This checks the format, runs your solution against your validator, and
   writes `problems/t3_NNN_slug.zip`.
5. Open a pull request adding exactly two things: the encrypted archive under
   `problems/` and your row in `INDEX.md` (printed by `pack.py`).

**Never put problem content in the PR title, description, comments, or any
commit.** GitHub retains commits forever, even after branch deletion — a leak
cannot be undone. A submission whose plaintext leaks is considered
contaminated and must be substantially reworked before resubmission.

## Evaluating on Tier 3

To run your own system on the collection:

```bash
python tools/unpack.py problems/t3_001_name.zip   # -> t3_001_name.plain/
python your_system_output.py | python t3_001_name.plain/ground_truth.py
```

The validator prints `{"valid": true/false, "message": "..."}`. If you
evaluate an LLM-based system, please do not paste problem text into publicly
logged services and report generated ASP code alongside final answers (see the
paper's discussion of Python-vs-ASP delegation).

## Review process

CI checks every PR automatically (blob-only guard, decryption, format checks,
solution-vs-validator run). The maintainer then reviews quality and novelty
and runs the baseline-agent hardness test. Expect a response within a few
weeks. Accepted problems are merged, credited, and included in the next
versioned Zenodo release.

## License and contact

All contributions are licensed under [Apache-2.0](LICENSE) (declared in each
submission's `metadata.yml`). Maintainer: Stefan Szeider, TU Wien —
sz@ac.tuwien.ac.at.
