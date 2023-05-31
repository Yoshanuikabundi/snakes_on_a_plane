"""Utilities for Snakes on a Plane"""

from pathlib import Path
from typing import Union

__all__ = ["get_git_root"]


def get_git_root(path: Union[str, Path]) -> Path:
    """Get root path of the Git repository containing the path provided.

    Raises
    ======

    git.InvalidGitRepositoryError
        If the provided path is not in a Git repository
    """
    from git.repo import Repo

    git_repo = Repo(path, search_parent_directories=True)
    git_root = git_repo.git.rev_parse("--show-toplevel")
    return Path(git_root)
