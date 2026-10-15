"""
Symbolic Explainable Artificial Intelligence 26/27

GROUP 18:
Artur Krystopchuk (104145) 
Sofia Ligeiro (116046) 

CSP-based solver for Alien Tiles, using MiniZinc
"""
import time

from pathlib import Path
from minizinc import Instance, Model, Solver
from alien_tiles.interface import Terminal

MODEL_PATH = Path(__file__).resolve().parent.parent / "model" / "alien_tiles.mzn"


def build_instance(game, solver_name="gecode"):
    """Create a MiniZinc instance for the given game's goal board"""
    instance = Instance(Solver.lookup(solver_name), Model(MODEL_PATH))

    instance["board_size"] = game.size
    instance["number_of_colours"] = game.number_of_colours
    instance["goal_board"] = game.goal_board

    return instance


def solve(game, solver_name="gecode", time_limit=None):
    """Return the optimal number of clicks per square as a list of lists"""
    instance = build_instance(game, solver_name)
    result = instance.solve(timeout=time_limit)

    if result.solution is None:
        raise ValueError("No solution was found for this puzzle instance")

    return result.solution.clicks_per_square



def run_model(game, terminal=None, solver_name="gecode", time_limit=None):
    """Solve the game and print the solution"""
    if terminal is None:
        terminal = Terminal()

    start = time.perf_counter()
    clicks = solve(game, solver_name=solver_name, time_limit=time_limit)
    seconds = time.perf_counter() - start

    terminal.display_solution(game, clicks, seconds)

    return clicks
