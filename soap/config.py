from typing import Mapping, Any, List, Union
from soap.utils import get_git_root
from soap.exceptions import ConfigError
import toml
from pathlib import Path


def _get_cfg_map(root_path: Path) -> Mapping[str, Any]:
    """Get the configuration map for SOAP in the current repository"""
    pyproject_path = root_path / "pyproject.toml"
    soaptoml_path = root_path / "soap.toml"

    if pyproject_path.exists():
        return toml.load(pyproject_path)["tool"]["soap"]
    else:
        return toml.load(soaptoml_path)


class Config:
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
            Alias(name, value) for name, value in cfg["aliases"].items()
        ]


class Env:
    def __init__(
        self, name: str, value: Union[str, Mapping[str, Any]], base_env_path: Path
    ):
        self.name: str = name

        if isinstance(value, str):
            value = {"yml_path": value}

        try:
            self.yml_path = Path(value["yml_path"])
        except KeyError:
            raise ConfigError(f"Value 'yml_path' missing from environment '{name}'")

        self.env_path = Path(value.get("env_path", base_env_path / name))


class Alias:
    def __init__(self, name, value: Union[str, Mapping[str, Any]]):
        self.name: str = name

        if isinstance(value, str):
            value = {"cmd": value}

        try:
            self.command = value["cmd"]
        except KeyError:
            raise ConfigError(f"Value 'cmd' missing from alias '{name}'")

        self.chdir = value.get("chdir", False)
        self.default_env = value.get("env", "dev")
        self.description = value.get("description", None)
