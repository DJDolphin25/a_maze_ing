## Instructions

Requires Python 3.10+.

Install the dev environment (linting, type-checking, tests, building):
```bash
pip install -e ".[dev]"
```

Run the program:
```bash
python3 a_maze_ing.py config.txt
```

Build the reusable `mazegen` package from source:
```bash
python3 -m build
```
This produces `mazegen-1.0.0-py3-none-any.whl` (and a `.tar.gz`) in `dist/`.
Install it on its own, elsewhere:
```bash
pip install mazegen-1.0.0-py3-none-any.whl
```

## Configuration file format

One `KEY=VALUE` pair per line. Lines starting with `#` are comments and are
ignored. Keys are case-insensitive.

| Key | Example | Meaning |
|---|---|---|
| `WIDTH` | `20` | maze width, in cells |
| `HEIGHT` | `15` | maze height, in cells |
| `ENTRY` | `0,0` | entry coordinates `x,y` — must be on the outer border |
| `EXIT` | `19,14` | exit coordinates `x,y` — on the border, different from `ENTRY` |
| `OUTPUT_FILE` | `maze.txt` | path to write the result to |
| `PERFECT` | `False` | `True` = single-path perfect maze; `False` = Pac-Man-style playable board |
| `SEED` *(optional)* | `42` | fixes the random seed, for a reproducible maze |

Any missing required key, bad syntax, or invalid value (wrong type, out of
bounds, impossible tuple) is reported with a clear message — the program
never crashes on a bad config file.

## Maze generation algorithm

**Perfect mode** uses a recursive backtracker, implemented with an explicit
stack instead of real function recursion (avoids Python's recursion-depth
limit on large mazes). From a starting cell, it repeatedly moves to a random
unvisited neighbor, opening the wall between them; when a cell has no
unvisited neighbor left, it backtracks (pops the stack) to the last cell
that still has one. Because it only ever connects to *unvisited* cells, the
result is guaranteed to be a spanning tree: every cell reachable, zero loops.

**Why this algorithm**: it's simple to reason about and verify (the
"no loop" guarantee falls directly out of the unvisited-only rule, not from
extra bookkeeping), produces uniformly winding mazes without a directional
bias, and the explicit-stack version scales to large grids without hitting
Python's recursion limit — a real constraint the naive recursive version
would run into.

**Non-perfect (Pac-Man) mode** starts from that same perfect maze, then
post-processes it in a fixed order:
1. carve the "42" pattern (close off cells forming the shape, unless the maze
   is too small, in which case it's skipped with a console warning),
2. reconnect anything that step split apart,
3. add extra walls to open independent routes (loops) between cells already
   connected — done carefully so no 3x3 (or larger) area ever ends up fully
   open,
4. keep opening walls at real dead-ends down to at most `max_dead_ends`
   (2 by default, matching the subject's own tolerance) — pass 0 for a
   fully "braided" board with no dead-end at all, though on a small grid
   that can force cells open on every side to reach it.

Building on the already-correct perfect generator, rather than writing a
separate loop-aware algorithm from scratch, means every step only has to
solve one small, independently-testable problem instead of getting all of
connectivity + loops + the open-area constraint right at once.

## The `mazegen` reusable module

```python
from mazegen import MazeGenerator, Wall, solve_bfs, serialize_maze

# Basic use - a perfect maze
gen = MazeGenerator(width=20, height=15, seed=42)
gen.generate_perfect(start_x=0, start_y=0)

# Or the Pac-Man-style mode (max_dead_ends=0 pushes for the fully
# braided "no dead-end at all" bonus instead of the default 2)
gen.generate_non_perfect(start_x=0, start_y=0, min_loops=2, max_dead_ends=0)

# The generated structure: a grid of Cell objects
cell = gen.grid[0][0]          # row 0, column 0
cell.x, cell.y                  # its coordinates
cell.walls                      # a Wall IntFlag - which of N/E/S/W are closed
cell.has_wall(Wall.NORTH)       # True/False

# A solution: shortest path from entry to exit, as 'N'/'E'/'S'/'W' moves
path = solve_bfs(gen.grid, entry=(0, 0), exit=(19, 14))

# Serialize to the subject's exact output format
text = serialize_maze(gen.grid, entry=(0, 0), exit=(19, 14), solution_path=path)
```

`Cell`/`Wall` (from `mazegen.cells`) and `validate_entry_exit`
(`mazegen.validation`) are also exported for anyone building their own
tooling around the generated structure.

## Resources

**Python language features**
- `Enum` / `IntFlag`: https://docs.python.org/3/library/enum.html
- `Enum` in depth: https://realpython.com/python-enum/
- Bitwise operators: https://realpython.com/python-bitwise-operators/
- Bitwise operators (GeeksforGeeks): https://www.geeksforgeeks.org/python-bitwise-operators/
- `dataclasses`: https://docs.python.org/3/library/dataclasses.html
- `dataclasses` in depth: https://realpython.com/python-data-classes/
- Custom exceptions: https://docs.python.org/3/tutorial/errors.html
- Exceptions in depth: https://realpython.com/python-exceptions/
- Context managers (`with`): https://docs.python.org/3/reference/compound_stmts.html#the-with-statement
- Context managers in depth: https://realpython.com/python-with-statement/
- `typing` module: https://docs.python.org/3/library/typing.html
- Type hints in depth: https://realpython.com/python-type-checking/
- `collections.deque`: https://docs.python.org/3/library/collections.html#collections.deque
- `random` module: https://docs.python.org/3/library/random.html
- `sys` module: https://docs.python.org/3/library/sys.html
- f-strings: https://docs.python.org/3/reference/lexical_analysis.html#f-strings

**Algorithms and data structures**
- BFS (GeeksforGeeks): https://www.geeksforgeeks.org/breadth-first-search-or-bfs-for-a-graph/
- BFS (Wikipedia): https://en.wikipedia.org/wiki/Breadth-first_search
- Backtracking (GeeksforGeeks): https://www.geeksforgeeks.org/backtracking-algorithms/
- Backtracking (Wikipedia): https://en.wikipedia.org/wiki/Backtracking
- Stacks (GeeksforGeeks): https://www.geeksforgeeks.org/stack-data-structure/
- Recursion vs. iteration: https://en.wikipedia.org/wiki/Recursion_(computer_science)
- Spanning trees: https://en.wikipedia.org/wiki/Spanning_tree
- Maze generation algorithms: https://en.wikipedia.org/wiki/Maze_generation_algorithm

**Terminal / display**
- ANSI escape codes: https://en.wikipedia.org/wiki/ANSI_escape_code
- Box-drawing Unicode characters: https://en.wikipedia.org/wiki/Box-drawing_character

**Project tooling**
- `pytest` (official docs): https://docs.pytest.org/en/stable/
- `pytest` in depth: https://realpython.com/pytest-python-testing/
- `mypy` (official docs): https://mypy.readthedocs.io/en/stable/
- `flake8` (official docs): https://flake8.pycqa.org/en/latest/

**Python packaging**
- Official packaging guide: https://packaging.python.org/en/latest/tutorials/packaging-projects/
- src-layout vs. flat-layout: https://packaging.python.org/en/latest/discussions/src-layout-vs-flat-layout/
- `setuptools` quickstart: https://setuptools.pypa.io/en/latest/userguide/quickstart.html
- PEP 517 (build backends): https://peps.python.org/pep-0517/
- PEP 518 (`pyproject.toml`): https://peps.python.org/pep-0518/
- PEP 621 (project metadata): https://peps.python.org/pep-0621/
- `venv` module: https://docs.python.org/3/library/venv.html
