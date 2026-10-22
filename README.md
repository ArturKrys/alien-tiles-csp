# Alien Tiles - CSP Project

Group 18 - Symbolic Explainable Artificial Intelligence 26/27

- Artur Krystopchuk (104145)
- Sofia Ligeiro (116046)

https://github.com/user-attachments/assets/ae9ae7c2-3593-4490-9cf3-08e2033a74e6

## Assignment requirements

The project asks us to solve a problem as a **Constraint Satisfaction Problem (CSP)** using Python and MiniZinc.

The chosen problem is:

- **CSPLib Problem 027 — Alien Tiles**
- Problem reference: <https://www.csplib.org/Problems/prob027/>

The program follows these steps:

1. Read a specific problem instance, either from standard input or a file.
2. Encode the instance as a MiniZinc CSP model.
3. Invoke the solver (Gecode).
4. Parse the solver output.
5. Write the solution to standard output.

## Project Structure
```
proj.py                         is the single entry point
alien_tiles/
              game.py               board state and click rules
              interface.py          setup parsing, human player and terminal output
              solver.py             builds the MiniZinc instance, solves, prints the solution
model/
              alien_tiles.mzn       the CSP model
examples/                           example setup files
dev/                                benchmark and tests
requirements.txt
```
- Human gameplay is supported.
- Model gameplay solves the puzzle with the CSP model and prints the clicks per square.
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

### Other ways to run

Without a setup file, the board is typed in at the prompt (standard input):

```bash
python3 proj.py --player model
# Board size: 3
# Number of colours: 3
# Goal row 1: 1 1 1
# Goal row 2: 1 0 0
# Goal row 3: 1 0 0
```

With no arguments at all, the program asks for the mode and then for the board:

```bash
python3 proj.py
```

A goal board that cannot be reached is reported as having no solution:

```bash
python3 proj.py examples/example_board_unsolvable.txt --player model
# Error: No solution was found for this puzzle instance
```

List every option:

```bash
python3 proj.py --help
```

Setup files contain `<size> <number_of_colours>` on the first line, followed by `<size>` rows of the goal board. Blank lines and lines starting with `#` are ignored (see `examples/`).

---
