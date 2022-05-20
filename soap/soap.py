from typing import Any, Mapping, Sequence
import toml
from soap.utils import get_git_root
import soap.conda
from pathlib import Path
import shutil
import filecmp


def get_cfg() -> Mapping[str, Any]:
    """Get the configuration map for SOAP in the current repository"""
    git_root = get_git_root(".")
    pyproject_path = git_root / "pyproject.toml"
    soaptoml_path = git_root / "soap.toml"
    cfg = {"env_path": git_root / ".soap"}
    if pyproject_path.exists():
        cfg.update(toml.load(pyproject_path)["tool"]["soap"])
    else:
        cfg.update(toml.load(soaptoml_path))
    return cfg


def prepare_env(env: str, cfg: Mapping[str, Any], ignore_cache=False):
    path_yml = Path(cfg["envs"][env])
    path_env = Path(cfg["env_path"] / env)
    # Cache the environment file and only construct the environment if it has changed
    path_cached_yml = path_env / path_yml.name
    if (
        ignore_cache
        or (not path_cached_yml.exists())
        or (not filecmp.cmp(path_cached_yml, path_yml))
    ):
        soap.conda.env_from_file(path_yml, path_env, install_current=True)
        shutil.copy2(path_yml, path_env)


def run_in_env(args: Sequence[str], env: str, cfg: Mapping[str, Any]):
    soap.conda.run_in_env(args, cfg["env_path"] / env)
