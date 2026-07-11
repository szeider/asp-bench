# Tier 3 Problem Index

Public metadata for all submissions. The fingerprint is the SHA-256 over the
plaintext files (printed by `pack.py`/`unpack.py`), so evaluators can confirm
they decrypted exactly what was reviewed. Status is one of `submitted`,
`candidate`, or `retired`.

**Reference 3-run record**: the maintainer runs the Tier-3 reference agent
(gpt-5.6-sol, see README) three times per problem and publishes the outcome:
solved runs / 3, then per-run execution calls, input tokens, and wall time.
Once enough candidates accumulate, these records define the Tier-3 goalpost.
For calibration, the reference agent solves the hardest Tier-1/2 problems
3/3 with 3–6 calls, ~120k tokens, ~2 minutes per run.

| Nr | Title | Authors | Aspects | Opt | Fingerprint (prefix) | Reference 3-run record | Status |
|---|---|---|---|---|---|---|---|
| 000 | Example: Minimum Vertex Cover | Stefan Szeider | OPT | yes | — (unencrypted, see `template/`) | — | template |
| 001 | Wildfire Response | Stefan Szeider | OPT, TEMP, RESOURCE, SPATIAL, RECURSIVE | yes | `61abac93513cae78` | solved 3/3 · calls 18/24/18 · in-tokens 369k/507k/347k · time 637/871/584 s | candidate |
