"""
Symbolic Explainable Artificial Intelligence 26/27

GROUP 18:
Artur Krystopchuk (104145) - arturkrystopchuk@tecnico.ulisboa.pt
Sofia Ligeiro (116046) - sofiamligeiro@tecnico.ulisboa.pt

Input handling and terminal interface for Alien Tiles.
"""

import os

from alien_tiles.game import AlienTilesGame


class Terminal:
    """Helper for readable terminal output"""

    COLOUR_CODES = (31, 32, 33, 34, 35, 36, 91, 92, 93, 94, 95, 96)
    RESET = "\033[0m"
    SEPARATOR_MIN_WIDTH = 40
    COLUMN_GAP = 6

    def __init__(self, use_colours=True):
        self.use_colours = use_colours and not os.environ.get("NO_COLOR")

    def colour(self, text, code):
        if not self.use_colours:
            return text
        return f"\033[{code}m{text}{self.RESET}"

    def board_colour(self, value):
        code = self.COLOUR_CODES[value % len(self.COLOUR_CODES)]
        return self.colour(f"[{value}]", code)

    def print_board(self, board, number_of_colours):
        for row in board:
            print(" ".join(self.board_colour(value) for value in row))

        legend = []
        for value in range(number_of_colours):
            legend.append(self.board_colour(value))
        print("Colours:", " ".join(legend))

    @staticmethod
    def plain_row(row):
        """Row without colour codes, used to measure the real width"""
        return " ".join(f"[{value}]" for value in row)

    def display_game(self, game):
        current = game.current_board
        goal = game.goal_board

        column_width = max(len(self.plain_row(row)) for row in goal)
        total_width = max(
            self.SEPARATOR_MIN_WIDTH, 2 * column_width + self.COLUMN_GAP
        )

        # Round separator
        title = f" Moves: {game.number_of_moves()} "
        print()
        print(self.colour(title.center(total_width, "="), 33))

        # Column headers
        header = "CURRENT BOARD".ljust(column_width + self.COLUMN_GAP)
        print(self.colour(header, 36) + self.colour("GOAL BOARD", 35))

        # Both boards side by side
        for current_row, goal_row in zip(current, goal):
            left = " ".join(self.board_colour(value) for value in current_row)
            right = " ".join(self.board_colour(value) for value in goal_row)
            padding = " " * (column_width - len(self.plain_row(current_row)) + self.COLUMN_GAP)
            print(left + padding + right)

        legend = " ".join(
            self.board_colour(value) for value in range(game.number_of_colours)
        )
        print()
        print("Colours:", legend)

    def click_cell(self, value, width):
        """A square of the click matrix: dim dot for zero, highlighted otherwise"""
        if value == 0:
            return self.colour(".".center(width), 90)
        return self.colour(f"[{value}]".center(width), 93)

    def display_solution(self, game, clicks, seconds=None):
        goal = game.goal_board
        column_width = max(len(self.plain_row(row)) for row in goal)
        total_width = max(
            self.SEPARATOR_MIN_WIDTH, 2 * column_width + self.COLUMN_GAP
        )
        cell_width = len(str(game.number_of_colours - 1)) + 2
        total_clicks = sum(sum(row) for row in clicks)

        print()
        print(self.colour(" MODEL SOLUTION ".center(total_width, "="), 32))

        header = "GOAL BOARD".ljust(column_width + self.COLUMN_GAP)
        print(self.colour(header, 35) + self.colour("CLICKS PER SQUARE", 93))

        for goal_row, click_row in zip(goal, clicks):
            left = " ".join(self.board_colour(value) for value in goal_row)
            padding = " " * (
                column_width - len(self.plain_row(goal_row)) + self.COLUMN_GAP
            )
            right = " ".join(self.click_cell(value, cell_width) for value in click_row)
            print(left + padding + right)

        steps = []
        for row_index, row in enumerate(clicks):
            for column_index, times in enumerate(row):
                if times:
                    label = f"({row_index + 1},{column_index + 1})"
                    steps.append(label + (f" x{times}" if times > 1 else ""))

        print()
        print("Click list:", ", ".join(steps))
        summary = f"Total clicks: {total_clicks}"
        if seconds is not None:
            summary += f"  (time: {seconds:.2f} s)"
        print(self.colour(summary, 32))


def read_non_empty_lines(file_path):
    """Read non-empty, non-comment lines from a setup file"""
    try:
        with open(file_path, "r", encoding="utf-8") as setup_file:
            lines = setup_file.readlines()
    except OSError as error:
        raise ValueError(f"Could not read setup file '{file_path}': {error}")

    return [
        line.strip()
        for line in lines
        if line.strip() and not line.strip().startswith("#")
    ]


def parse_setup_lines(lines, source_name):
    """ 
    Create a game from setup lines
    Setup format: '<size> <number_of_colours>' followed by <size> goal-board rows
    """
    if not lines:
        raise ValueError(f"The setup from {source_name} is empty")

    first_line = lines[0].split()
    if len(first_line) != 2:
        raise ValueError("The first line must be: <size> <number_of_colours>")

    try:
        size = int(first_line[0])
        number_of_colours = int(first_line[1])
    except ValueError:
        raise ValueError("The first line must contain two integers")

    if size <= 0:
        raise ValueError("The board size must be greater than zero")
    if number_of_colours <= 1:
        raise ValueError("The number of colours must be greater than one")

    board_lines = lines[1:]
    if len(board_lines) != size:
        raise ValueError(
            f"Expected {size} goal-board rows, but found {len(board_lines)}"
        )

    goal_board = []

    for row_number, line in enumerate(board_lines, start=1):
        values = line.split()
        if len(values) != size:
            raise ValueError(f"Goal-board row {row_number} must contain {size} values")

        try:
            row = [int(value) for value in values]
        except ValueError:
            raise ValueError(f"Goal-board row {row_number} must contain integers only")

        if any(value < 0 or value >= number_of_colours for value in row):
            raise ValueError(
                f"Goal-board values must be between 0 and {number_of_colours - 1}"
            )

        goal_board.append(row)

    return AlienTilesGame(size, number_of_colours, goal_board)


def read_setup_file(file_path):
    return parse_setup_lines(read_non_empty_lines(file_path), file_path)


def ask_for_integer(prompt, minimum_value=None):
    """Read an integer from standard input"""
    while True:
        try:
            value = int(input(prompt).strip())
        except ValueError:
            print("Please enter an integer")
            continue

        if minimum_value is not None and value < minimum_value:
            print(f"Please enter an integer at least {minimum_value}")
            continue

        return value


def read_setup_manually():
    """Read a puzzle setup from standard input"""
    print("Manual puzzle setup")
    size = ask_for_integer("Board size: ", minimum_value=1)
    number_of_colours = ask_for_integer("Number of colours: ", minimum_value=2)

    print(f"Enter {size} goal-board rows with {size} values per row")
    print(f"Values must be between 0 and {number_of_colours - 1}")

    goal_board = []

    for row_number in range(1, size + 1):
        while True:
            values = input(f"Goal row {row_number}: ").split()

            if len(values) != size:
                print(f"Enter exactly {size} values")
                continue

            try:
                row = [int(value) for value in values]
            except ValueError:
                print("Every value must be an integer")
                continue

            if any(value < 0 or value >= number_of_colours for value in row):
                print(f"Values must be between 0 and {number_of_colours - 1}.")
                continue

            goal_board.append(row)
            break

    return AlienTilesGame(size, number_of_colours, goal_board)


def choose_player(requested_player):
    """Choose human or model mode"""
    if requested_player is not None:
        return requested_player

    while True:
        player = input("Choose player (human/model): ").strip().lower()
        if player in ("human", "model"):
            return player
        print("Please enter 'human' or 'model'")


def print_help(terminal):
    print(terminal.colour("Commands", 33))
    print("  <row> <column>  click a square (coordinates start at 1)")
    print("  u                undo the last click")
    print("  r                reset the board")
    print("  h                show this help")
    print("  q                quit the game")


def run_human(game, terminal):
    """Run the terminal interface for a human player"""
    print(terminal.colour("\nAlien Tiles", 1))
    print_help(terminal)

    while True:
        terminal.display_game(game)

        if game.is_solved():
            print(terminal.colour("Solved!", 32))
            return

        command = input("Your move: ").strip().lower()

        if command == "q":
            print("Game ended")
            return

        if command == "h":
            print_help(terminal)
            continue

        if command == "u":
            if game.undo():
                print(terminal.colour("Last click undone", 33))
            else:
                print("There are no clicks to undo")
            continue

        if command == "r":
            game.reset()
            print(terminal.colour("Board reset", 33))
            continue

        coordinates = command.split()
        if len(coordinates) != 2:
            print("Enter two coordinates, or use one of the commands above")
            continue

        try:
            row = int(coordinates[0]) - 1
            column = int(coordinates[1]) - 1
        except ValueError:
            print("Coordinates must be integers")
            continue

        if not game.is_inside_board(row, column):
            print("That square is outside the board")
            continue

        game.click_square(row, column)
