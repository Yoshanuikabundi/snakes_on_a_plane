"""Configuration for Snakes on a Plane"""

from typing import Any, Dict, Union
from soap.utils import get_git_root
from soap.exceptions import MissingConfigFileError
import toml
from pathlib import Path
from schema import Schema, Optional, Or, And, Use, Literal

__all__ = [
    "Config",
    "Env",
    "Alias",
]


def _get_name(schema):
    while not isinstance(schema, str):
        schema = schema.schema
    return schema


DEFAULT_ENV = "test"


ENV_SCHEMA = Schema(
    {
        Literal(
            "yml_path",
            description="Path to YAML file defining the environment.",
        ): And(str, Use(Path)),
        Optional(
            Literal(
                "env_path",
                description="Prefix of the new environment. Defaults to `.soap/<name of environment>`",
            ),
            default=None,
        ): And(str, Use(Path)),
        Optional(
            Literal(
                "install_current",
                description="If True, install the current project in this environment after all dependencies.",
            ),
            default=True,
        ): bool,
        Optional(
            Literal(
                "additional_channels",
                description="Channels to prepend to the environment file's channel list.",
            ),
            default=[],
        ): [str],
        Optional(
            Literal(
                "additional_dependencies",
                description="Packages and constraints to add to the environment file.",
            ),
            default=[],
        ): [str],
    }
)
ENV_SCHEMA_JSON = ENV_SCHEMA.json_schema("`[envs]`")

_ENV_DEFAULTS = {
    _get_name(key): key.default for key in ENV_SCHEMA.schema if hasattr(key, "default")
}

ALIAS_SCHEMA = Schema(
    {
        Literal("cmd", description="The command to alias"): str,
        Optional(
            Literal(
                "chdir",
                description="If True, always run this command in the git repository root directory.",
            ),
            default=False,
        ): bool,
        Optional(
            Literal(
                "env",
                description="The environment in which to run this command when the --env argument is not passed.",
            ),
            default=DEFAULT_ENV,
        ): str,
        Optional(
            Literal(
                "description",
                description="A description of this command for the --help argument.",
            ),
            default="",
        ): str,
        Optional(
            Literal(
                "passthrough_args",
                description="If True, SOAP will pass any unrecognised arguments through to the aliased command.",
            ),
            default=False,
        ): bool,
    }
)
ALIAS_SCHEMA_JSON = ALIAS_SCHEMA.json_schema("`[aliases]`")

_ALIAS_DEFAULTS = {
    _get_name(key): key.default
    for key in ALIAS_SCHEMA.schema
    if hasattr(key, "default")
}

CFG_SCHEMA = Schema(
    {
        Optional("envs", default={}): Or(
            {},
            {
                str: Or(
                    And(str, Use(lambda s: _ENV_DEFAULTS | {"yml_path": Path(s)})),
                    ENV_SCHEMA,
                )
            },
        ),
        Optional("aliases", default={}): Or(
            {},
            {
                str: Or(
                    And(str, Use(lambda s: _ALIAS_DEFAULTS | {"cmd": s})),
                    ALIAS_SCHEMA,
                )
            },
        ),
    }
)
CFG_SCHEMA_JSON = CFG_SCHEMA.json_schema("Snakes On A Plane: `soap.toml`")


def _get_cfg_map(root_path: Path) -> Dict[str, Any]:
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
    TomlDecodeError
        If the file was found but is not valid TOML
    SchemaError
        If the config file is valid TOML but does not match the SOAP configuration
        schema.
    """
    pyproject_path = root_path / "pyproject.toml"
    soaptoml_path = root_path / "soap.toml"

    if soaptoml_path.exists():
        data = toml.load(soaptoml_path)
    elif pyproject_path.exists():
        data = toml.load(pyproject_path)["tool"]["soap"]
    else:
        raise MissingConfigFileError(
            f"pyproject.toml and soap.toml both missing from {root_path}"
        )

    return CFG_SCHEMA.validate(data)


class Config:
    """
    Configuration for a SOAP project

    Attributes
    ==========

    envs
        Mapping from environment names to environment ``Env`` objects. The map
        key matches the ``.name`` attribute of the environment.
    aliases
        List of ``Alias`` objects defined in the project.

    Raises
    ======

    MissingConfigFileError
        If ``pyproject.toml`` and ``soap.toml`` are both missing from the root
        path.
    TomlDecodeError
        If the file was found but is not valid TOML
    SchemaError
        If the config file is valid TOML but does not match the SOAP configuration
        schema.
    """

    def __init__(
        self,
        git_root: Union[Path, None] = None,
        cfg: Union[Dict[str, Any], None] = None,
    ):
        if git_root is None:
            git_root = get_git_root(".")

        if cfg is None:
            cfg = _get_cfg_map(git_root)

        self.envs = {
            name: Env(name, value, git_root) for name, value in cfg["envs"].items()
        }
        self.aliases = [Alias(name, value) for name, value in cfg["aliases"].items()]

    def __repr__(self):
        return f"<Config with aliases {self.aliases!r} and envs {self.envs!r}>"


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
    """

    def __init__(
        self,
        name: str,
        value: Dict[str, Any],
        package_root: Path,
    ):
        self.name: str = name
        self.package_root = Path(package_root).absolute()

        self.yml_path = (
            value["yml_path"]
            if value["yml_path"].is_absolute()
            else self.package_root / value["yml_path"]
        )

        self.env_path = (
            Path(".soap") / self.name
            if value["env_path"] is None
            else value["env_path"]
        )
        if not self.env_path.is_absolute():
            self.env_path = self.package_root / self.env_path

        self.install_current = value["install_current"]
        self.additional_channels = value["additional_channels"]
        self.additional_dependencies = value["additional_dependencies"]

    def __repr__(self):
        return (
            f"Env(name={self.name!r}, value={{"
            + f"yml_path: {self.yml_path!r}, "
            + f"env_path: {self.env_path!r}, "
            + f"package_root: {self.package_root!r}, "
            + f"install_current: {self.install_current!r},"
            + f"additional_channels: {self.additional_channels!r},"
            + f"additional_dependencies: {self.additional_dependencies!r},"
            + f"}})"
        )


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
    """

    def __init__(
        self,
        name,
        value: Dict[str, Any],
    ):
        self.name = name
        self.command = value["cmd"]
        self.chdir = value["chdir"]
        self.default_env = value["env"]
        self.description = value["description"] or "Alias for `" + self.command + "`"
        self.passthrough_args = value["passthrough_args"]

    def __repr__(self):
        return (
            f"Alias(name={self.name!r}, value={{"
            + f"cmd: {self.command!r}, "
            + f"chdir: {self.chdir!r}, "
            + f"env: {self.default_env!r}, "
            + f"description: {self.description!r}}}, "
            + f"passthrough_args: {self.passthrough_args!r}"
            + f"}})"
        )
