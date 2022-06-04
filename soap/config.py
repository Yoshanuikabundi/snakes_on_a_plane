"""Configuration for Snakes on a Plane"""

from typing import Mapping, Any, List, Union
from soap.utils import get_git_root
from soap.exceptions import InvalidConfigError, MissingConfigFileError
import toml
from pathlib import Path

__all__ = [
    "Config",
    "Env",
    "Alias",
]


def _get_cfg_map(root_path: Path) -> Mapping[str, Any]:
    """
    Get the configuration map for SOAP

    Parameters
    ==========

    root_path
        The path in which to look for a configuration file

    Raises
    ======

    MissingConfigFileError
        If ``pyproject.toml`` and ``soap.toml`` are both missing from the root
        path.
    """
    pyproject_path = root_path / "pyproject.toml"
    soaptoml_path = root_path / "soap.toml"

    if soaptoml_path.exists():
        return toml.load(soaptoml_path)
    elif pyproject_path.exists():
        return toml.load(pyproject_path)["tool"]["soap"]
    else:
        raise MissingConfigFileError(
            f"pyproject.toml and soap.toml both missing from {root_path}"
        )


class Config:
    """
    Configuration for a SOAP project

    Attributes
    ==========

    git_root
        The root directory of the Git repository.
    envs
        Mapping from environment names to environment ``Env`` objects. The map
        key matches the ``.name`` attribute of the environment.
    aliases
        List of ``Alias`` objects defined in the project.

    Raises
    ======

    InvalidConfigError
        If an environment is missing a ``yml_path`` or an alias is missing a
        ``command``
    MissingConfigFileError
        If ``pyproject.toml`` and ``soap.toml`` are both missing from the
        current Git repository root directory.


    """

    def __init__(self):
        self.git_root = get_git_root(".")
        cfg = _get_cfg_map(self.git_root)

        env_path = Path(cfg.get("env_path", ".soap"))
        if not env_path.is_absolute():
            env_path = self.git_root / env_path

        self.envs: Mapping[str, Env] = {
            name: Env(name, value, env_path) for name, value in cfg["envs"].items()
        }
        self.aliases: List[Alias] = [
            Alias(name, value) for name, value in cfg.get("aliases", {}).items()
        ]


class Env:
    """
    Configuration for a single environment.

    Attributes
    ==========

    name
        Name of the environment
    yml_path
        Path to the Conda environment YAML file
    env_path
        Path to the environment prefix
    install_current
        True if the current project should be installed 
        in the environment with ``pip install -e .`` 


    Raises
    ======

    InvalidConfigError
        If the environment is missing a ``yml_path``
    """

    def __init__(
        self,
        name: str,
        value: Union[str, Mapping[str, Any]],
        base_env_path: Path,
    ):
        self.name: str = name

        if isinstance(value, str):
            value = {"yml_path": value}

        try:
            self.yml_path = Path(value["yml_path"])
        except KeyError:
            raise InvalidConfigError(
                f"Value 'yml_path' missing from environment '{name}'"
            )

        self.env_path = Path(value.get("env_path", base_env_path / name))
        self.install_current: bool = bool(value.get("install_current", True))

    def __repr__(self):
        return f"Env(name={self.name!r}, value={{yml_path: {self.yml_path!r}, env_path: {self.env_path!r}}})"


class Alias:
    """
    Configuration for a single alias.

    Attributes
    ==========

    name
        Name of the alias. This is the subcommand used to execute the alias.
    command
        The command being aliased.
    chdir
        If True, the command will be run from the Git repository root directory,
        rather than the current directory.
    default_env
        The environment to run the alias in if none is specified on the command
        line.

    Raises
    ======

    InvalidConfigError
        If the alias is missing a ``command``.
    """

    def __init__(self, name, value: Union[str, Mapping[str, Any]]):
        self.name: str = name

        if isinstance(value, str):
            value = {"cmd": value}

        try:
            self.command = value["cmd"]
        except KeyError:
            raise InvalidConfigError(f"Value 'cmd' missing from alias '{name}'")

        self.chdir = value.get("chdir", False)
        self.default_env = value.get("env", "dev")
        self.description = value.get("description", None)
        self.passthrough_args = value.get("passthrough_args", False)

    def __repr__(self):
        return f"Alias(name={self.name!r}, value={{cmd: {self.command!r}, chdir: {self.chdir!r}, env: {self.default_env!r}, description: {self.description!r}}})"
