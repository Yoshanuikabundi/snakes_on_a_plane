"""Utilities for Snakes on a Plane"""

from git.repo import Repo
from pathlib import Path
from typing import Union


def get_git_root(path: Union[str, Path]) -> Path:
    """Get root path of the Git repository containing the path provided.

    Raises
    ======

    git.InvalidGitRepositoryError
        If the provided path is not in a Git repository
    """
    git_repo = Repo(path, search_parent_directories=True)
    git_root = git_repo.git.rev_parse("--show-toplevel")
    return Path(git_root)
