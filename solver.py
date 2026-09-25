"""
Symbolic Explainable Artificial Intelligence 26/27

GROUP 18:
Artur Krystopchuk (104145) 
Sofia Ligeiro (116046) 

CSP-based solver for Alien Tiles, using MiniZinc
"""

from pathlib import Path
from minizinc import Instance, Model, Solver

MODEL_PATH = Path(__file__).resolve().parent / "alien_tiles.mzn"


def build_instance(game, solver_name="gecode"):
    """Create a MiniZinc instance for the given game's goal board"""
    model = Model(MODEL_PATH)
    solver = Solver.lookup(solver_name)
    instance = Instance(solver, model)

    instance["n"] = game.size
    instance["c"] = game.number_of_colours
    instance["goal"] = game.goal_board

    return instance


def solve(game, solver_name="gecode", time_limit=None):
    """Solve the puzzle and return the click counts as a list of lists"""
    instance = build_instance(game, solver_name)
    result = instance.solve(timeout=time_limit)

    if result.solution is None:
        raise ValueError("No solution was found for this puzzle instance.")

    return result.solution.clicks


def print_solution(clicks, number_of_colours):
    """Print the click counts per square and the total number of clicks."""
    print("Solution (number of clicks per square):")
    for row in clicks:
        print(" ".join(str(value) for value in row))

    total_clicks = sum(value for row in clicks for value in row)
    print(f"\nTotal clicks: {total_clicks}")


def run_model(game, solver_name="gecode", time_limit=None):
    """Solve the current game's goal with the CSP model and report it."""
    clicks = solve(game, solver_name=solver_name, time_limit=time_limit)
    print_solution(clicks, game.number_of_colours)
    return clicks
