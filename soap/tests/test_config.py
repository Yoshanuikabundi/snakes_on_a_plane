"""
Tests for the config module
"""

# Import package, test suite, and other packages as needed
import pytest
import toml
from pathlib import Path
from copy import deepcopy
from typing import Any

import soap.config as cfg

MAXIMALIST_VALIDATED = {
    "envs": {
        "test": {
            "yml_path": Path("devtools/conda-envs/test_env.yml"),
            "env_path": None,
            "install_current": True,
            "additional_channels": [],
            "additional_dependencies": [],
        },
        "docs": {
            "yml_path": Path("devtools/conda-envs/docs_env.yml"),
            "env_path": None,
            "install_current": False,
            "additional_channels": [],
            "additional_dependencies": [],
        },
        "user": {
            "yml_path": Path("devtools/conda-envs/user_env.yml"),
            "env_path": Path("/home/someone/conda/envs/soap-env"),
            "install_current": True,
            "additional_channels": [],
            "additional_dependencies": [],
        },
        "gromacs": {
            "yml_path": Path("devtools/conda-envs/user_env.yml"),
            "env_path": None,
            "install_current": True,
            "additional_channels": ["bioconda"],
            "additional_dependencies": ["gromacs"],
        },
    },
    "aliases": {
        "list": {
            "cmd": "conda list",
            "chdir": False,
            "env": "test",
            "description": "",
            "passthrough_args": False,
        },
        "greet": {
            "cmd": "echo hello world",
            "chdir": False,
            "env": "test",
            "description": "",
            "passthrough_args": False,
        },
        "docs": {
            "cmd": "sphinx-build -j auto docs docs/_build/html",
            "chdir": True,
            "env": "docs",
            "description": "Build the docs with Sphinx",
            "passthrough_args": True,
        },
        "npm": {
            "cmd": "npm",
            "chdir": Path("js"),
            "env": "user",
            "description": "",
            "passthrough_args": True,
        },
    },
}


def test_maximalist_toml():
    """Check that a maximalist toml file validates correctly."""
    data = toml.load("soap/tests/data/maximalist.toml")
    validated = cfg.ConfigModel.model_validate(data)
    assert validated.model_dump() == MAXIMALIST_VALIDATED


def test_maximalist_cfg():
    root_dir = Path("/home/someone/project")

    config_dict: Any = deepcopy(MAXIMALIST_VALIDATED)
    config = cfg.ConfigModel.model_validate(config_dict, context={"root_dir": root_dir})

    assert config.envs["test"].env_path == root_dir / ".soap/test"
    assert config.envs["docs"].env_path == root_dir / ".soap/docs"
    assert config.envs["user"].env_path == Path("/home/someone/conda/envs/soap-env")

    assert config.aliases["docs"].chdir == root_dir
