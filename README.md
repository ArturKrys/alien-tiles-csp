# Alien Tiles - CSP Project

## Assignment requirements

The project asks us to solve a problem as a **Constraint Satisfaction Problem (CSP)** using Python and MiniZinc.

The chosen problem is:

- **CSPLib Problem 027 — Alien Tiles**
- Problem reference: <https://www.csplib.org/Problems/prob027/>

The program follows these steps:

1. Read a specific problem instance, either from standard input or a file.
2. Encode the instance as a MiniZinc CSP model.
4. Parse the solver output.
5. Write the solution to standard output.

## Current implementation

The current code provides a playable version of the Alien Tiles game, with the following features:

- `proj.py` is the single entry point.
- `game.py` contains the board state and move rules.
- `interface.py` contains Human input handling and the coloured terminal interface.
- `alien_tiles.mzn` — the CSP model: `clicks[i,j]` (number of times each square is clicked, domain `0..c-1`) subject to one constraint per square, minimizing the total number of clicks.
- `solver.py` builds a MiniZinc `Instance` from an `AlienTilesGame` (injecting `n`, `c`, `goal`), invokes the solver, parses `result.solution.clicks`, and prints the solution.
- `test_solver.py` — exhaustive tests for small `(n, c)` pairs: brute-forces every possible click pattern to get the true optimal click count and the exact set of reachable goal boards, then checks the solver matches the true optimum exactly and correctly reports "no solution" for unreachable goals.

- Human gameplay is supported.
- Model gameplay currently raises a placeholder error.
- Puzzle setups can be entered manually or loaded from a `.txt` file.

## Running the current version

The project uses Python 3.12+ and MiniZinc (recommended version 2.10.1) with the Gecode solver, plus the `minizinc-python` package.

1. Install the MiniZinc bundle for your OS

2. Set up the Python environment:

```bash
python3 -m venv .venv
source .venv/bin/activate # on windows: .\.venv\Scripts\activate
pip install -r requirements.txt
```

## Running

Solve a puzzle with the CSP solver:

```bash
python3 proj.py examples/example_board_1.txt --player model
```

Play interactively instead:

```bash
python3 proj.py examples/example_board_1.txt --player human
```

If `--player` is omitted, the program asks interactively which mode to use:

```bash
python3 proj.py examples/example_board_1.txt
# Choose player (human/model):
```

Use `--no-colour` if ANSI colours are not supported by the terminal.

---

## Optimizations

Old solution

```minizinc
int: n; int: c;
array[1..n,1..n] of int: goal;
array[1..n,1..n] of var 0..c-1: clicks;
constraint forall(r in 1..n, s in 1..n)(
  (sum(j in 1..n)(clicks[r,j]) + sum(i in 1..n)(clicks[i,s]) - clicks[r,s])
    mod c == goal[r,s]);
solve minimize sum(i,j in 1..n)(clicks[i,j]);
```

### Optimization 1: rearranging the constraint

The colour a square ends up with only depends on three numbers:

> colour of (row, column) = (clicks in that row) + (clicks in that column) - clicks_per_square[row, column]   (mod number_of_colours)

We subtract `clicks_per_square[row, column]` because the square belongs to both its row and its column, so otherwise it would be counted twice.

We call the row total (mod number_of_colours) `row_clicks_mod_colours[row]`, and the column total `column_clicks_mod_colours[column]`. The rule becomes:

> goal_board[row, column] = row_clicks_mod_colours[row] + column_clicks_mod_colours[column] - clicks_per_square[row, column] (mod number_of_colours)

Moving terms around:

> clicks_per_square[row, column] = row_clicks_mod_colours[row] + column_clicks_mod_colours[column] - goal_board[row, column] (mod number_of_colours)

So once we know a row's total and a column's total, the number of clicks on the square where they cross is fixed. There is nothing left to guess for that square.

The original model had to guess the clicks of every square: $n^2$ variables, so up to $c^{n^2}$ combinations. The new model only has to guess the row and column totals: $2n$ variables, so up to $c^{2n}$ combinations ($n$ is the board size, $c$ the number of colours). For a 6×6 board with 3 colours, that is $3^{12} \approx 530\,000$ combinations instead of $3^{36} \approx 1.5 \times 10^{17}$.

### Optimization 2: telling the solver what to guess first

By default the solver chooses for itself which variables to guess. We tell it to guess only the row and column totals (`int_search(row_clicks_mod_colours ++ column_clicks_mod_colours, ...)`). Every square's clicks then follow automatically from the formula above. Without this instruction the solver also guesses square clicks, which wastes time: on a 6×6 board with 3 colours it took 2.06 s (161 865 dead ends) without it, against 0.09 s (7 316 dead ends) with it.

### Optimization 3: symmetry breaking

Sometimes the goal board has two identical rows. Take first example board:

    1 1 1
    1 0 0
    1 0 0

Rows 2 and 3 are the same. If we take a solution and swap all the clicks of row 2 with all the clicks of row 3, the result still reaches the goal with the same number of clicks. It is a second solution that is just a copy of the first, and without help the solver would check both.

To avoid this, we add a rule: when two rows of the goal board are identical, the first one's total must not be bigger than the second one's. That way the solver only looks at one of the two copies. We do the same for identical columns.

The same idea works when the goal board looks the same flipped along its diagonal (row 1 equals column 1, row 2 equals column 2, and so on), like the example above. Flipping the solution along the diagonal gives another copy, so we keep only one of the two.

These rules never remove the best answer, only its duplicates. They only help when the goal board has identical rows, identical columns, or diagonal symmetry. Most random boards have none of these, which is why the gain shows up on the "symmetric" boards in the table but not on the "random" ones.

### Results

| goal board | size | colours | original | improved, no symmetry breaking | improved |
|---|---|---|---|---|---|
| random | 4 | 3 | 0.013s / 2168 | 0.003s / 404 | 0.002s / 275 |
| random | 5 | 3 | >30s | 0.018s / 1947 | 0.020s / 1947 |
| random | 6 | 3 | >30s | 0.079s / 7374 | 0.086s / 7374 |
| random | 8 | 3 | >30s | 1.358s / 90416 | 1.462s / 90416 |
| random | 5 | 4 | >30s | 0.100s / 10171 | 0.095s / 10171 |
| random | 7 | 4 | >30s | 12.498s / 1006384 | 12.657s / 1006384 |
| symmetric | 6 | 4 | >30s | 0.580s / 53927 | 0.106s / 8298 |
| symmetric | 7 | 4 | >30s | 3.450s / 262040 | 0.066s / 3938 |
| symmetric | 8 | 4 | >30s | 18.667s / 1209725 | 1.620s / 87913 |

> Note it's showing the time and the number of dead ends until it found the solution.

Each cell shows the solve time and the number of dead ends (failures). A dead end is a guess the solver had to undo because it led to a contradiction or could not beat the best solution found so far. The dead-end count does not depend on how fast the computer is, so it is a fairer comparison than time alone. ">30s" means the solver had not finished after 30 seconds.

Optimizations 1 and 2 give most of the speed-up: every board except the smallest went from not finishing in 30 seconds to finishing in under 13. Symmetry breaking adds a further 5–50× speed-up on symmetric boards and makes no difference on random ones.

### Things we tried that did not help

- Replacing `mod` with an extra "how many times it wrapped around" variable per square: about 2× faster than the original, but far slower than optimization 1.
- Adding an extra redundant constraint on the total number of clicks: same number of dead ends, slightly slower.
- Letting the solver pick the row/column with the fewest options first (`first_fail`) instead of going in order: no difference.


---

For final delivery delete [.venv](.venv), [.gitignore](.gitignore), [benchmark.py](benchmark.py) and [test_solver.py](test_solver.py)
