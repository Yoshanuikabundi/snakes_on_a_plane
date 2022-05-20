from git.repo import Repo
from pathlib import Path
from typing import Union


def get_git_root(path: Union[str, Path]) -> Path:
    """Get the path to the root path of the git repository provided."""
    git_repo = Repo(path, search_parent_directories=True)
    git_root = git_repo.git.rev_parse("--show-toplevel")
    return Path(git_root)
