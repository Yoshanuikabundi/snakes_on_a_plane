"""Exceptions for Snakes on a Plane"""

__all__ = [
    "InvalidConfigError",
    "MissingConfigFileError",
]


class InvalidConfigError(Exception):
    """Raised when a configuration file is valid TOML but has an invalid schema."""

    pass


class MissingConfigFileError(Exception):
    """Raised when a configuration file is missing."""

    pass
