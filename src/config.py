# src/config.py
"""Reads and validates the KEY=VALUE config file a_maze_ing.py needs.

This is separate from mazegen/ on purpose: config.txt is specific to
this program (a_maze_ing.py), not something a future project reusing
the mazegen package would need.
"""
from dataclasses import dataclass
from typing import Dict, Optional, Tuple

from .mazegen.validation import validate_entry_exit

REQUIRED_KEYS = ("WIDTH", "HEIGHT", "ENTRY", "EXIT", "OUTPUT_FILE", "PERFECT")

TRUE_VALUES = {"true", "1", "yes"}
FALSE_VALUES = {"false", "0", "no"}


class ConfigError(Exception):
    """Raised when the config file is missing, malformed, or invalid.

    Always carries a clear, human-readable message - a_maze_ing.py can
    catch this and print it directly, per the subject's "never crash,
    always a clear error message" requirement.
    """


@dataclass
class MazeConfig:
    """The parsed, validated content of a config file."""

    width: int
    height: int
    entry: Tuple[int, int]
    exit: Tuple[int, int]
    output_file: str
    perfect: bool
    seed: Optional[int] = None


def load_config(path: str) -> MazeConfig:
    """Reads, parses and validates a config file into a MazeConfig.

    Args:
        path: path to the config file.

    Returns:
        A fully validated MazeConfig.

    Raises:
        ConfigError: if the file is missing, has bad syntax, is missing
            a required key, or has an invalid/impossible value.
    """
    pairs = _read_key_value_pairs(path)

    missing = [key for key in REQUIRED_KEYS if key not in pairs]
    if missing:
        raise ConfigError(
            f"missing required key(s) in {path}: {', '.join(missing)}."
        )

    width = _parse_positive_int(pairs["WIDTH"], "WIDTH")
    height = _parse_positive_int(pairs["HEIGHT"], "HEIGHT")
    entry = _parse_coordinates(pairs["ENTRY"], "ENTRY")
    exit = _parse_coordinates(pairs["EXIT"], "EXIT")
    perfect = _parse_bool(pairs["PERFECT"], "PERFECT")
    output_file = pairs["OUTPUT_FILE"]
    if not output_file:
        raise ConfigError("OUTPUT_FILE must not be empty.")

    seed = None
    if "SEED" in pairs:
        try:
            seed = int(pairs["SEED"])
        except ValueError:
            raise ConfigError(f"SEED={pairs['SEED']!r} must be an integer.")

    try:
        validate_entry_exit(width, height, entry, exit)
    except ValueError as error:
        raise ConfigError(str(error))

    return MazeConfig(
        width=width,
        height=height,
        entry=entry,
        exit=exit,
        output_file=output_file,
        perfect=perfect,
        seed=seed,
    )


def _read_key_value_pairs(path: str) -> Dict[str, str]:
    """Reads KEY=VALUE lines from path, skipping blanks and # comments."""
    pairs: Dict[str, str] = {}
    try:
        with open(path, encoding="utf-8") as config_file:
            for line_number, raw_line in enumerate(config_file, start=1):
                line = raw_line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" not in line:
                    raise ConfigError(
                        f"{path}:{line_number}: {line!r} is not a valid "
                        "KEY=VALUE line."
                    )
                key, _, value = line.partition("=")
                pairs[key.strip()] = value.strip()
    except FileNotFoundError:
        raise ConfigError(f"config file not found: {path}")
    except OSError as error:
        raise ConfigError(f"could not read config file {path}: {error}")
    return pairs


def _parse_positive_int(value: str, key: str) -> int:
    """Parses value as a positive int, raising ConfigError otherwise."""
    try:
        parsed = int(value)
    except ValueError:
        raise ConfigError(f"{key}={value!r} must be an integer.")
    if parsed <= 0:
        raise ConfigError(f"{key}={value!r} must be a positive integer.")
    return parsed


def _parse_coordinates(value: str, key: str) -> Tuple[int, int]:
    """Parses 'x,y' into (x, y) ints."""
    parts = value.split(",")
    if len(parts) != 2:
        raise ConfigError(f"{key}={value!r} must be in 'x,y' format.")
    try:
        return int(parts[0]), int(parts[1])
    except ValueError:
        raise ConfigError(
            f"{key}={value!r} must be two integers separated by a comma."
        )


def _parse_bool(value: str, key: str) -> bool:
    """Parses True/False (and a few common variants), case-insensitive."""
    normalized = value.strip().lower()
    if normalized in TRUE_VALUES:
        return True
    if normalized in FALSE_VALUES:
        return False
    raise ConfigError(f"{key}={value!r} must be True or False.")
