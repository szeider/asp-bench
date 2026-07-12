# Example: Minimum Vertex Cover

*(This is the format template. A real Tier-3 problem would be much harder — see
SUBMISSION_GUIDE.md for the hardness criterion.)*

## Problem Statement

A security company must place guards on the junctions of a tunnel system so
that every tunnel is watched. A tunnel is watched if a guard stands on at
least one of its two endpoints. Guards are expensive: find a placement that
watches every tunnel with the minimum possible number of guards.

## Instance

The tunnel system has junctions 1 to 6 and the following seven tunnels:

- (1,2), (1,3), (2,3)
- (3,4)
- (4,5), (4,6), (5,6)

## Output Format

Print a single JSON object to standard output:

```json
{"cover": [<junction>, <junction>, ...]}
```

where `cover` lists the junctions on which guards are placed, in any order.

## Requirements

- Every tunnel must have a guard on at least one endpoint.
- The number of guards must be **minimum** (this is an optimization problem;
  a feasible but suboptimal placement is invalid).

## Solution Requirement

*(Standard block — include verbatim in every Tier-3 problem.)*

Solve this with a **clingo (ASP) encoding**, not a Python search. Your program
may use Python only to read the instance, print the JSON result, and — if
needed — re-run the *same* encoding while sweeping a single numeric bound
(e.g. lower a target until UNSAT). All search and all "no better solution
exists" reasoning must be done by clingo inside the ASP program (`#minimize`,
disjunction/saturation, constraints). Computing counterexamples, cores, or
candidates in Python and feeding them back into clingo (CEGAR, hitting sets,
branch-and-bound, guess-and-check) does **not** count, even if the printed
answer is correct.

<!-- Replace this comment with the canary line: run `python tools/pack.py canary`
     and paste its output verbatim as the last line of this file. -->
