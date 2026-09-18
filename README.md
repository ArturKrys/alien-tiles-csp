# Alien Tiles - CSP Project

## Assignment requirements

The project asks us to solve a problem as a **Constraint Satisfaction Problem (CSP)** using Python and MiniZinc.

The chosen problem is:

- **CSPLib Problem 027 — Alien Tiles**
- Problem reference: <https://www.csplib.org/Problems/prob027/>

The program follows these steps:

1. Read a specific problem instance, either from standard input or a file.
2. Encode the instance as a MiniZinc CSP model. (Not done yet.)
3. Invoke a MiniZinc solver. (Not done yet.)
4. Parse the solver output. (Not done yet.)
5. Write the solution to standard output.

## Current implementation

The current code provides a playable version of the Alien Tiles game, with the following features:

- `proj.py` is the single entry point.
- `game.py` contains the board state and move rules.
- `interface.py` contains Human input handling and the coloured terminal interface.
- `solver.py` Future MiniZinc/model integration
- Human gameplay is supported.
- Model gameplay currently raises a placeholder error.
- Puzzle setups can be entered manually or loaded from a `.txt` file.

## Running the current version

The project uses Python 3.12 and currently has no third-party dependencies.

```bash
python3 -m venv .venv
source .venv/bin/activate # on windows: .\.venv\Scripts\activate
pip install -r requirements.txt
```

Run with an example setup file:

```bash
python3 proj.py examples/example_board_1.txt --player human
```

Or enter a setup manually:

```bash
python3 proj.py --player human
```

Use `--no-colour` if ANSI colours are not supported by the terminal.
