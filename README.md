# Alien Tiles - CSP Project

Group 18 - Symbolic Explainable Artificial Intelligence 26/27

- Artur Krystopchuk (104145)
- Sofia Ligeiro (116046)

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
