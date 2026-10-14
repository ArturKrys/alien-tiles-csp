"""
Symbolic Explainable Artificial Intelligence 26/27

GROUP 18:
Artur Krystopchuk (104145) - arturkrystopchuk@tecnico.ulisboa.pt
Sofia Ligeiro (116046) - sofiamligeiro@tecnico.ulisboa.pt

Exhaustive correctness checks for the Alien Tiles CSP encoding.

test_solver.py only checks that the solver's solution is VALID and no
worse than an arbitrary non-optimal generator. It does not prove the
solver finds the true minimum, and it never exercises an unreachable
goal board (not every goal is necessarily reachable from the all-zero
board -- whether it is depends on the rank, over Z_c, of the linear
map induced by clicking).

This script brute-forces the ENTIRE space of click patterns for small
(n, c) pairs, giving:
  - the true optimal (minimum) click count for every reachable goal,
    so we can check the solver's answer against ground truth exactly;
  - the exact set of unreachable goal boards (if any), so we can check
    the solver correctly reports "no solution" for them instead of
    silently returning something wrong.

Brute force is O(c ** (n * n)), so only run this for small n, c.

"""


import itertools
 
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from alien_tiles.game import AlienTilesGame
from alien_tiles.solver import solve
 
SIZE_COLOUR_PAIRS = ((2, 2), (2, 3), (2, 4), (2, 5), (3, 2), (3, 3))
SAMPLE_LIMIT = 15  

REACHABILITY_SWEEP_PAIRS = (
    [(2, c) for c in range(2, 9)] + [(3, c) for c in range(2, 5)]
)
 
 
def effect_board(size, colours, click_matrix):
    """Pure-Python mirror of the .mzn constraint (independent cross-check)."""
    board = [[0] * size for _ in range(size)]
    for r in range(size):
        for s in range(size):
            row_sum = sum(click_matrix[r][j] for j in range(size))
            col_sum = sum(click_matrix[i][s] for i in range(size))
            board[r][s] = (row_sum + col_sum - click_matrix[r][s]) % colours
    return board
 
 
def brute_force_reachable(size, colours):
    """Every reachable goal board (as a tuple key) mapped to its true minimum clicks."""
    best = {}
    cells = size * size
    for combo in itertools.product(range(colours), repeat=cells):
        click_matrix = [list(combo[i * size:(i + 1) * size]) for i in range(size)]
        goal = effect_board(size, colours, click_matrix)
        goal_key = tuple(tuple(row) for row in goal)
        total = sum(combo)
        if goal_key not in best or total < best[goal_key]:
            best[goal_key] = total
    return best
 
 
def all_possible_boards(size, colours):
    cells = size * size
    for combo in itertools.product(range(colours), repeat=cells):
        yield tuple(combo[i * size:(i + 1) * size] for i in range(size))
 
 
def check_optimality(size, colours, reachable):
    """Sample reachable goals and check the solver finds the EXACT minimum."""
    checked = 0
    failures = 0
    for goal_key, true_min in reachable.items():
        if checked >= SAMPLE_LIMIT:
            break
        goal_board = [list(row) for row in goal_key]
        game = AlienTilesGame(size, colours, goal_board)
        clicks = solve(game)
        solver_total = sum(value for row in clicks for value in row)
 
        if solver_total != true_min:
            failures += 1
            print(
                f"  MISMATCH goal={goal_board} solver={solver_total} "
                f"true_min={true_min}"
            )
        checked += 1
 
    print(f"  Optimality: {checked - failures}/{checked} exact matches with brute force")
    return failures == 0
 
 
def check_unsat_detection(size, colours, reachable):
    """Find goals brute force never produced, and check the solver rejects them."""
    unreachable_samples = []
    for board in all_possible_boards(size, colours):
        if board not in reachable:
            unreachable_samples.append([list(row) for row in board])
            if len(unreachable_samples) >= 5:
                break
 
    if not unreachable_samples:
        print("  Every goal board is reachable for this (size, colours); no UNSAT case here.")
        return True
 
    print(f"  Found {len(unreachable_samples)} unreachable board(s); checking solver rejects them...")
    failures = 0
    for goal_board in unreachable_samples:
        game = AlienTilesGame(size, colours, goal_board)
        try:
            solve(game)
            print(f"    FAIL: solver found a solution for unreachable {goal_board}")
            failures += 1
        except ValueError:
            print(f"    OK: solver correctly reported no solution for {goal_board}")
 
    return failures == 0
 
 
def reachability_only_sweep(pairs):
    """Fast, solver-free sweep to see how %reachable varies with n and c."""
    print("\n=== Reachability-only sweep (no solver calls) ===")
    for size, colours in pairs:
        total = colours ** (size * size)
        reachable = brute_force_reachable(size, colours)
        pct = 100 * len(reachable) / total
        is_prime = colours > 1 and all(colours % d for d in range(2, colours))
        tag = "prime" if is_prime else "composite"
        print(f"  n={size} c={colours} ({tag}): {len(reachable)}/{total} reachable ({pct:.1f}%)")
 
 
def main():
    all_ok = True
 
    reachability_only_sweep(REACHABILITY_SWEEP_PAIRS)
 
    for size, colours in SIZE_COLOUR_PAIRS:
        total_boards = colours ** (size * size)
        print(f"\n=== size={size} colours={colours} ({total_boards} possible boards) ===")
 
        reachable = brute_force_reachable(size, colours)
        print(f"  Reachable goal boards: {len(reachable)} / {total_boards} "
              f"({100 * len(reachable) / total_boards:.1f}%)")
 
        ok_optimal = check_optimality(size, colours, reachable)
        ok_unsat = check_unsat_detection(size, colours, reachable)
        all_ok = all_ok and ok_optimal and ok_unsat
 
    print("\nAll exhaustive checks passed." if all_ok else "\nSome checks FAILED.")
    return 0 if all_ok else 1
 
 
if __name__ == "__main__":
    raise SystemExit(main())
 