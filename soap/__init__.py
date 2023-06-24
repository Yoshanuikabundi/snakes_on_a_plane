"""Snakes on a Plane: Conda meets Cargo"""

# Add imports here
from soap._soap import prepare_env, run_in_env
from soap.config import Config, Alias, Env

# Import the version from setuptools_scm _version module
from soap._version import version as VERSION
from soap._version import version_tuple as VERSION_TUPLE

__all__ = [
    "prepare_env",
    "run_in_env",
    "Config",
    "Alias",
    "Env",
    "VERSION",
    "VERSION_TUPLE",
]
