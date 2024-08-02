"""Configuration for Snakes on a Plane"""

from typing import Any, Dict, Union, List
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


ROOT_DIR_KEY = "ROOT_DIR"


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
                description=(
                    "Where to run the command. True for the git repository root"
                    + " directory, False for the working directory, or a path"
                    + " relative to the root directory.",
                ),
            ),
            default=False,
        ): Or(bool, And(str, Use(Path))),
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


def _get_cfg_map(leaf_path: Union[None, Path] = None) -> Dict[str, Any]:
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
    if pyproject_path is None and len(soaptoml_paths) == 0:
        raise MissingConfigFileError(
            f"Couldn't find pyproject.toml or any soap.toml files searching up"
            + f" the file tree from {leaf_path}"
        )

    # Load the data from all config files and combine them
    data = _combine_cfg_maps([toml.load(path) for path in soaptoml_paths])
    if pyproject_path:
        pyproject_data = toml.load(pyproject_path).get("tool", {}).get("soap", {})
        data = _combine_cfg_maps([data, pyproject_data])

    # Validate against the schema
    data = CFG_SCHEMA.validate(data)

    # Make sure we haven't added an entry with this name to the config schema,
    # then add the root path to the data
    assert ROOT_DIR_KEY not in (k.key for k in CFG_SCHEMA.schema)
    data[ROOT_DIR_KEY] = root_path

    return data


def _combine_cfg_maps(data: List[Dict[str, None]]) -> Dict[str, None]:
    """Combine a list of toml data files into one

    At the moment this just returns the first nonempty dictionary."""
    # TODO: Combine multiple dictionaries
    for d in data:
        if d:
            return d


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
        leaf_path: Union[Path, None] = None,
        cfg: Union[Dict[str, Any], None] = None,
    ):
        if cfg is None:
            cfg = _get_cfg_map(leaf_path)

        self.root_dir = cfg[ROOT_DIR_KEY]
        self.envs = {
            name: Env(name, value, self.root_dir) for name, value in cfg["envs"].items()
        }
        self.aliases = [
            Alias(name, value, self.root_dir) for name, value in cfg["aliases"].items()
        ]

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
        root_dir: Path,
    ):
        self.name = name
        self.command = value["cmd"]

        self.chdir: Path | None
        if not value["chdir"]:
            self.chdir = None
        elif value["chdir"] is True:
            self.chdir = root_dir
        else:
            self.chdir = root_dir / value["chdir"]

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
