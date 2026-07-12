# Tier 3 Problem Index

Public metadata for all submissions. The fingerprint is the SHA-256 over the
plaintext files (printed by `pack.py`/`unpack.py`), so evaluators can confirm
they decrypted exactly what was reviewed. Status is one of `submitted`,
`candidate`, or `retired`.

**Reference 3-run record**: the maintainer runs the Tier-3 reference agent
(gpt-5.6-sol, see README) three times per problem and publishes the outcome:
solved runs / 3, then per-run execution calls, input tokens, and wall time.
A run counts as **solved only if it produces a clingo encoding** (the Core rule
in SUBMISSION_GUIDE.md) whose output passes the ground truth; a correct answer
obtained by a Python search (CEGAR, hitting sets, branch-and-bound,
guess-and-check) is **not** a solve — such runs are noted parenthetically but
do not count. Once enough candidates accumulate, these records define the
Tier-3 goalpost. For calibration, the reference agent solves the hardest
Tier-1/2 problems 3/3 with 3–6 calls, ~120k tokens, ~2 minutes per run.

| Nr | Title | Authors | Aspects | Opt | Fingerprint (prefix) | Reference 3-run record | Status |
|---|---|---|---|---|---|---|---|
| 000 | Example: Minimum Vertex Cover | Stefan Szeider | OPT | yes | — (unencrypted, see `template/`) | — | template |
| 001 | Wildfire Response | Stefan Szeider | OPT, TEMP, RESOURCE, SPATIAL, RECURSIVE | yes | `61abac93513cae78` | solved 3/3 · calls 18/24/18 · in-tokens 369k/507k/347k · time 637/871/584 s | candidate |
| 002 | Jamming the Valley Network | Stefan Szeider | OPT, QUANT | yes | `37c324ce53faa6b5` | solved 0/3 (runs 1–2 output-correct but not an ASP encoding — Python CEGAR; run 3 timeout) · calls 6/6/— · in-tokens 140k/144k/— · time 136/866/1200 s | candidate |
