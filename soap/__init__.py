"""Conda meets Cargo"""

# Add imports here
from soap.soap import prepare_env, run_in_env
from soap.config import Config, Alias, Env

__all__ = ["prepare_env", "run_in_env", "Config", "Alias", "Env"]

# Handle versioneer
from ._version import get_versions

versions = get_versions()
__version__ = versions["version"]
__git_revision__ = versions["full-revisionid"]
del get_versions, versions
