"""Utilities for Snakes on a Plane"""

from pathlib import Path
from typing import Union

import yaml

__all__ = ["get_git_root", "yaml_file_to_dict", "dict_to_yaml_str"]


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


def dict_to_yaml_str(data: dict, **kwargs) -> str:
    return yaml.dump(
        data,
        Dumper=_YamlIndentDumper,
        default_flow_style=False,
        **kwargs,
    )


def yaml_file_to_dict(filename: Path, **kwargs) -> dict:
    return yaml.safe_load(filename.read_text())


class _YamlIndentDumper(yaml.Dumper):
    def increase_indent(self, flow=False, indentless=False):
        return super().increase_indent(flow, False)
