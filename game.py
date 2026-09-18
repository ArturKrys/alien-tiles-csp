"""
Symbolic Explainable Artificial Intelligence 26/27

GROUP 18:
Artur Krystopchuk (104145) - arturkrystopchuk@tecnico.ulisboa.pt
Sofia Ligeiro (116046) - sofiamligeiro@tecnico.ulisboa.pt

Game state and rules for Alien Tiles.
"""

from copy import deepcopy


class AlienTilesGame:
    """Represent one Alien Tiles puzzle."""

    def __init__(self, size, number_of_colours, goal_board):
        self.size = size
        self.number_of_colours = number_of_colours
        self.goal_board = goal_board
        self.current_board = self.empty_board()
        self.previous_boards = []

    def empty_board(self):
        """Create the all-zero starting board."""
        return [[0 for _ in range(self.size)] for _ in range(self.size)]

    def click_square(self, row, column):
        """Click a zero-based square and update its row and column."""
        if not self.is_inside_board(row, column):
            raise ValueError("The selected square is outside the board.")

        self.previous_boards.append(deepcopy(self.current_board))

        for board_row in range(self.size):
            for board_column in range(self.size):
                is_same_row = board_row == row
                is_same_column = board_column == column

                if is_same_row or is_same_column:
                    old_value = self.current_board[board_row][board_column]
                    self.current_board[board_row][board_column] = (
                        old_value + 1
                    ) % self.number_of_colours

    def undo(self):
        """Undo the latest click, if one exists."""
        if not self.previous_boards:
            return False

        self.current_board = self.previous_boards.pop()
        return True

    def reset(self):
        """Return the puzzle to its all-zero starting board."""
        self.current_board = self.empty_board()
        self.previous_boards = []

    def is_inside_board(self, row, column):
        return 0 <= row < self.size and 0 <= column < self.size

    def is_solved(self):
        return self.current_board == self.goal_board

    def number_of_moves(self):
        return len(self.previous_boards)
