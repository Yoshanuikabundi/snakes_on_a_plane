"""Configuration for Snakes on a Plane"""

from typing import Any, Dict, Union, List, Optional
from soap.utils import get_git_root
from soap.exceptions import MissingConfigFileError
import toml
from pathlib import Path
from pydantic import Field, FilePath, field_validator, FieldValidationInfo

from ._models import BaseModel

__all__ = [
    "ConfigModel",
    "EnvModel",
    "AliasModel",
]


DEFAULT_ENV = "test"


class EnvModel(BaseModel):
    yml_path: FilePath
    """Path to YAML file defining the environment."""
    env_path: Optional[Path] = None  # TODO: Figure out how to remove the Optional
    """Prefix of the new environment. Defaults to `.soap/<name of environment>`"""
    install_current: bool = True
    """If True, install the current project in this environment after all dependencies."""
    additional_channels: list[str] = Field(default_factory=list)
    """Channels to prepend to the environment file's channel list."""
    additional_dependencies: list[str] = Field(default_factory=list)
    """Packages and constraints to add to the environment file."""

    @field_validator("yml_path", "env_path")
    def root_paths(cls, value, info: FieldValidationInfo):
        if value.is_absolute():
            return value

        if isinstance(info.context, dict):
            root_dir = Path(info.context.get("root_dir", "."))
        else:
            root_dir = Path()

        return root_dir / value


class AliasModel(BaseModel):
    command: str = Field(..., alias="cmd")
    """The command to run."""

    chdir: Union[bool, Path] = False
    """
    Where to run the command.

    True for the git repository root directory, False for the working directory,
    or a path relative to the root directory.
    """

    default_env: str = Field(DEFAULT_ENV, alias="env")
    """The environment in which to run this command when the --env argument is not passed."""

    description: str = ""
    """A description of this command for the --help argument."""

    passthrough_args: bool = False
    """If True, SOAP will pass any unrecognised arguments through to the aliased command."""

    @field_validator("chdir")
    def set_chdir(cls, value, info: FieldValidationInfo):
        if isinstance(info.context, dict):
            root_dir = Path(info.context.get("root_dir", "."))
        else:
            root_dir = Path()

        if not value:
            return value
        elif value is True:
            return root_dir
        else:
            return root_dir / value


class ConfigModel(BaseModel):
    envs: dict[str, EnvModel] = Field(default_factory=dict)
    """Environments to run commands in."""
    aliases: dict[str, AliasModel] = Field(default_factory=dict)
    """Aliases for commands."""

    @classmethod
    def from_file_tree(
        cls,
        leaf_path: Union[Path, None] = None,
        cfg: Union[Dict[str, Any], None] = None,
    ):
        if cfg is not None:
            return cls.model_validate(cfg)

        root_dir, cfg = _get_cfg_map(leaf_path)

        return cls.model_validate(cfg, context={"root_dir": root_dir})

    @field_validator("envs", mode="before")
    def proc_string_envs(cls, value, info: FieldValidationInfo):
        try:
            return {
                name: {"yml_path": value} if isinstance(value, str) else value
                for name, value in value.items()
            }
        except AttributeError:
            return value

    @field_validator("envs", mode="after")
    def set_env_paths(cls, value, info: FieldValidationInfo):
        if isinstance(info.context, dict):
            root_dir = Path(info.context.get("root_dir", "."))
        else:
            root_dir = Path()
        for name, model in value.items():
            if model.env_path is None:
                model.env_path = root_dir / ".soap" / name
            model._package_root = root_dir
        return value

    @field_validator("aliases", mode="before")
    def proc_string_aliases(cls, value, info: FieldValidationInfo):
        try:
            return {
                name: {"cmd": value} if isinstance(value, str) else value
                for name, value in value.items()
            }
        except AttributeError:
            return value


def _get_cfg_map(leaf_path: Union[None, Path] = None) -> tuple[Path, Dict[str, Any]]:
    """
    Get the configuration map for SOAP

    Parameters
    ==========

    root_path
        The path in which to look for a configuration file

    Raises
    ======

    MissingConfigFileError
        If no ``pyproject.toml`` and ``soap.toml`` files can be found by walking
        up the file tree from leaf_path
    TomlDecodeError
        If any discovered config file was not valid TOML
    SchemaError
        If a config file is valid TOML but does not match the SOAP configuration
        schema.
    """
    # Walk up the file tree looking for config files
    leaf_path = (
        Path(".").absolute() if leaf_path is None else Path(leaf_path).absolute()
    )
    pyproject_path = None  # Path to the pyproject.toml describing the project
    root_path = None  # Root path of the project
    soaptoml_paths = []  # Paths of all soap.toml files
    for path in (leaf_path, *leaf_path.parents):
        # Remember the top level pyproject file and record it as the root dir
        pyproject = path / "pyproject.toml"
        if pyproject.exists():
            pyproject_path = pyproject
            root_path = path

        # Remember all soap.toml files, and the directory of the topmost one if
        # we don't have a better guess at the root path
        soaptoml = path / "soap.toml"
        if soaptoml.exists():
            soaptoml_paths.append(soaptoml)
            if pyproject_path is None:
                root_path = path

    # Try and get the git root directory, as its our best guess at the root
    # directory
    try:
        root_path = get_git_root(".")
    except Exception as e:
        # TODO: Use a warning library for this
        print(
            "Running Git failed:",
            e.__traceback__,
            f"Using {root_path} as root directory",
            sep="\n",
        )

    # Raise an error if we haven't found any config files
    if root_path is None:
        raise MissingConfigFileError(
            f"Couldn't find pyproject.toml or any soap.toml files searching up"
            + f" the file tree from {leaf_path}"
        )

    # Load the data from all config files and combine them
    data = _combine_cfg_maps([toml.load(path) for path in soaptoml_paths])
    if pyproject_path:
        pyproject_data = toml.load(pyproject_path)
        pyproject_data.get("tool", {}).get("soap", {})
        data = _combine_cfg_maps([data, pyproject_data])

    return root_path, data


def _combine_cfg_maps(data: List[Dict[str, None]]):
    """Combine a list of toml data files into one

    At the moment this just returns the first dictionary."""
    # TODO: Combine multiple dictionaries
    return data[0]
