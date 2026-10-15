"""
Symbolic Explainable Artificial Intelligence 26/27

GROUP 18:
Artur Krystopchuk (104145) - arturkrystopchuk@tecnico.ulisboa.pt
Sofia Ligeiro (116046) - sofiamligeiro@tecnico.ulisboa.pt

Compare the original model with the improved alien_tiles.mzn and print a
Markdown table, ready for the report.

Each cell shows "solve time / failures". Failures are the dead ends the
solver hit during search (choices it had to undo); fewer failures means
less wasted search, and unlike time it does not depend on the computer.

How to run (from the project root, with the virtual environment active):

    python3 dev/benchmark.py        # 30 s limit per run
    python3 dev/benchmark.py 10     # custom limit in seconds
"""

import random
import sys
from datetime import timedelta
from pathlib import Path

from minizinc import Instance, Model, Solver, Status

HERE = Path(__file__).resolve().parent

# The first version of the model, kept here so it can be compared without
# needing a second .mzn file.
ORIGINAL_MODEL = """
int: board_size; int: number_of_colours;
array[1..board_size,1..board_size] of int: goal_board;
array[1..board_size,1..board_size] of var 0..number_of_colours-1: clicks_per_square;
constraint forall(row, column in 1..board_size)(
  (sum(other_column in 1..board_size)(clicks_per_square[row,other_column])
   + sum(other_row in 1..board_size)(clicks_per_square[other_row,column])
   - clicks_per_square[row,column]) mod number_of_colours == goal_board[row,column]);
solve minimize sum(clicks_per_square);
"""


def goal_board_from_clicks(clicks_per_square, number_of_colours):
    """The board you get from the all-zero board after these clicks."""
    board_size = len(clicks_per_square)
    return [
        [(sum(clicks_per_square[row])
          + sum(clicks_per_square[other_row][column] for other_row in range(board_size))
          - clicks_per_square[row][column]) % number_of_colours
         for column in range(board_size)]
        for row in range(board_size)
    ]


def random_goal_board(board_size, number_of_colours, random_generator):
    """A random goal board that is guaranteed to be solvable."""
    clicks_per_square = [[random_generator.randrange(number_of_colours)
                          for _ in range(board_size)] for _ in range(board_size)]
    return goal_board_from_clicks(clicks_per_square, number_of_colours)


def symmetric_goal_board(board_size, number_of_colours, identical_rows, random_generator):
    """A solvable goal board that looks the same flipped along its diagonal and
    whose first `identical_rows` rows (and columns) are identical, so the
    symmetry breaking has something to work with."""
    clicks_per_square = [[0] * board_size for _ in range(board_size)]
    for row in range(board_size):
        for column in range(row, board_size):
            clicks_per_square[row][column] = clicks_per_square[column][row] = \
                random_generator.randrange(number_of_colours)
    for row in range(1, identical_rows):
        clicks_per_square[row] = clicks_per_square[0][:]
    for row in range(board_size):
        for column in range(1, identical_rows):
            clicks_per_square[row][column] = clicks_per_square[row][0]
    return goal_board_from_clicks(clicks_per_square, number_of_colours)


def run(model, board_size, number_of_colours, goal_board, time_limit_seconds,
        break_symmetries=None):
    instance = Instance(Solver.lookup("gecode"), model)
    instance["board_size"] = board_size
    instance["number_of_colours"] = number_of_colours
    instance["goal_board"] = goal_board
    if break_symmetries is not None:
        instance["break_symmetries"] = break_symmetries
    result = instance.solve(timeout=timedelta(seconds=time_limit_seconds), statistics=True)

    if result.status not in (Status.OPTIMAL_SOLUTION, Status.UNSATISFIABLE):
        return f">{time_limit_seconds}s"
    seconds = result.statistics["solveTime"].total_seconds()
    return f"{seconds:.3f}s / {result.statistics['failures']}"


def main():
    time_limit_seconds = int(sys.argv[1]) if len(sys.argv) > 1 else 30
    random_generator = random.Random(2026)

    original_model = Model()
    original_model.add_string(ORIGINAL_MODEL)
    improved_model = Model(HERE.parent / "model" / "alien_tiles.mzn")

    test_cases = [
        ("random", board_size, number_of_colours,
         random_goal_board(board_size, number_of_colours, random_generator))
        for board_size, number_of_colours in [(4, 3), (5, 3), (6, 3), (8, 3), (5, 4), (7, 4)]
    ]
    test_cases += [
        ("symmetric", board_size, number_of_colours,
         symmetric_goal_board(board_size, number_of_colours, identical_rows, random_generator))
        for board_size, number_of_colours, identical_rows in [(6, 4, 3), (7, 4, 5), (8, 4, 4)]
    ]

    print(f"Time limit {time_limit_seconds}s per run. Each cell: solve time / failures.\n")
    print("| goal board | size | colours | original | improved, no symmetry breaking | improved |")
    print("|---|---|---|---|---|---|")
    for kind, board_size, number_of_colours, goal_board in test_cases:
        cells = [
            run(original_model, board_size, number_of_colours, goal_board, time_limit_seconds),
            run(improved_model, board_size, number_of_colours, goal_board, time_limit_seconds,
                break_symmetries=False),
            run(improved_model, board_size, number_of_colours, goal_board, time_limit_seconds),
        ]
        print(f"| {kind} | {board_size} | {number_of_colours} | " + " | ".join(cells) + " |",
              flush=True)


if __name__ == "__main__":
    main()
