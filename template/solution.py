#!/usr/bin/env python3
"""Example solution for "Example: Minimum Vertex Cover".

Uses the clingo Python API (clingo==5.8.*) and prints the solution JSON to
stdout. The whole script must finish within 60 seconds; individual solver
calls should stay within the 20-second design limit of ASP-Bench.
"""

import json
from clingo import Control

PROGRAM = """
vertex(1..6).
edge(1,2). edge(1,3). edge(2,3). edge(3,4). edge(4,5). edge(4,6). edge(5,6).

{ in_cover(V) : vertex(V) }.
:- edge(X,Y), not in_cover(X), not in_cover(Y).

#minimize { 1,V : in_cover(V) }.
#show in_cover/1.
"""

best_cover = []


def on_model(model):
    global best_cover
    best_cover = sorted(sym.arguments[0].number
                        for sym in model.symbols(shown=True))


def main():
    ctl = Control()
    ctl.configuration.solve.opt_mode = "opt"
    ctl.add("base", [], PROGRAM)
    ctl.ground([("base", [])])
    ctl.solve(on_model=on_model)
    print(json.dumps({"cover": best_cover}))


if __name__ == "__main__":
    main()
