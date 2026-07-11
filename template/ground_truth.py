#!/usr/bin/env python3
"""Ground truth validator for "Example: Minimum Vertex Cover".

Reads the solution JSON from stdin and prints
{"valid": true/false, "message": "..."} to stdout.

Must be plain Python 3, standard library only (no clingo, no third-party
imports). It must accept EVERY correct solution, not just one reference
solution. For optimization problems the known optimum is pinned in the
module-level constant EXPECTED_OPTIMAL, and feasible but suboptimal
solutions are rejected.
"""

import json
import sys

# Replace this comment with the canary comment line:
# run `python tools/pack.py canary` and paste its output after a leading '# '.

EXPECTED_OPTIMAL = 4

VERTICES = set(range(1, 7))
EDGES = [(1, 2), (1, 3), (2, 3), (3, 4), (4, 5), (4, 6), (5, 6)]


def fail(message):
    print(json.dumps({"valid": False, "message": message}))
    sys.exit(0)


def main():
    try:
        solution = json.load(sys.stdin)
    except json.JSONDecodeError:
        fail("input is not valid JSON")

    if not isinstance(solution, dict) or "cover" not in solution:
        fail("missing required field 'cover'")

    cover = solution["cover"]
    if not isinstance(cover, list) or not all(isinstance(v, int) for v in cover):
        fail("'cover' must be a list of integers")

    cover_set = set(cover)
    if not cover_set <= VERTICES:
        fail(f"cover contains unknown junctions: {sorted(cover_set - VERTICES)}")

    for x, y in EDGES:
        if x not in cover_set and y not in cover_set:
            fail(f"tunnel ({x},{y}) is not watched")

    if len(cover_set) != EXPECTED_OPTIMAL:
        fail(f"cover has size {len(cover_set)}, but the optimum is {EXPECTED_OPTIMAL}")

    print(json.dumps({"valid": True,
                      "message": f"optimal vertex cover of size {EXPECTED_OPTIMAL}"}))


if __name__ == "__main__":
    main()
