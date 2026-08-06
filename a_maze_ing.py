#!/usr/bin/env python3
# a_maze_ing.py
"""Generates and solves a maze from a config file, and writes the result.

Usage:
    python3 a_maze_ing.py config.txt
"""
import sys
from typing import List

from src.config import ConfigError, load_config
from src.display import run_interactive
from src.mazegen import MazeGenerator, serialize_maze, solve_bfs


def main(argv: List[str]) -> int:
    """Runs the whole pipeline: config -> generate -> solve -> write.

    Args:
        argv: sys.argv, so argv[0] is the program name and argv[1]
            should be the config file path.

    Returns:
        Process exit code: 0 on success, 1 on any handled error.
    """
    if len(argv) != 2:
        print(f"Usage: python3 {argv[0]} <config_file>")
        return 1

    config_path = argv[1]

    try:
        config = load_config(config_path)
    except ConfigError as error:
        print(f"Error: {error}")
        return 1

    generator = MazeGenerator(config.width, config.height, seed=config.seed)
    if config.perfect:
        generator.generate_perfect(config.entry[0], config.entry[1])
    else:
        generator.generate_non_perfect(config.entry[0], config.entry[1])

    path = solve_bfs(generator.grid, config.entry, config.exit)
    output = serialize_maze(generator.grid, config.entry, config.exit, path)

    try:
        with open(config.output_file, "w", encoding="utf-8") as out_stream:
            out_stream.write(output)
    except OSError as error:
        print(f"Error: could not write {config.output_file}: {error}")
        return 1

    print(f"Maze written to {config.output_file}")

    # Only open the interactive menu when attached to a real terminal -
    # a Moulinette or test run redirecting stdin/stdout must not hang
    # waiting for keyboard input.
    if sys.stdin.isatty():
        run_interactive(
            generator,
            path,
            config.width,
            config.height,
            config.entry,
            config.exit,
            config.perfect,
        )

    return 0


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv))
    except Exception as error:  # last-resort safety net, never crash
        print(f"Unexpected error: {error}")
        sys.exit(1)
