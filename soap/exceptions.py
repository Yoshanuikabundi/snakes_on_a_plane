"""Exceptions for Snakes on a Plane"""

__all__ = [
    "MissingConfigFileError",
]


class MissingConfigFileError(Exception):
    """Raised when a configuration file is missing."""

    pass
