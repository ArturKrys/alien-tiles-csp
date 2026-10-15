"""
Symbolic Explainable Artificial Intelligence 26/27

GROUP 18:
Artur Krystopchuk (104145) - arturkrystopchuk@tecnico.ulisboa.pt
Sofia Ligeiro (116046) - sofiamligeiro@tecnico.ulisboa.pt

Entry point for Alien Tiles (CSPLib 027)
"""

import argparse

from alien_tiles.interface import (
    Terminal,
    choose_player,
    read_setup_file,
    read_setup_manually,
    run_human,
)
from alien_tiles.solver import run_model


def build_argument_parser():
    parser = argparse.ArgumentParser(description="Play or solve Alien Tiles.")
    
    parser.add_argument(
        "setup_file",
        nargs="?",
        help="optional .txt setup file; if omitted, setup is read from standard input",
    )
    parser.add_argument(
        "--player",
        choices=("human", "model"),
        help="player mode; if omitted, the program asks interactively",
    )
    parser.add_argument(
        "--no-colour",
        action="store_true",
        help="disable ANSI colours in terminal output",
    )
    return parser


def main():
    arguments = build_argument_parser().parse_args()

    try:
        player = choose_player(arguments.player)

        if arguments.setup_file:
            game = read_setup_file(arguments.setup_file)
        else:
            game = read_setup_manually()

        if player == "model":
            run_model(game, Terminal(use_colours=not arguments.no_colour))
        else:
            run_human(game, Terminal(use_colours=not arguments.no_colour))

    except (ValueError, EOFError) as error:
        print(f"Error: {error}")
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
