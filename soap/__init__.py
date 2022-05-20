"""Conda meets Cargo"""

# Add imports here
from soap.soap import get_cfg, prepare_env, run_in_env

__all__ = ["get_cfg", "prepare_env", "run_in_env"]

# Handle versioneer
from ._version import get_versions

versions = get_versions()
__version__ = versions["version"]
__git_revision__ = versions["full-revisionid"]
del get_versions, versions
