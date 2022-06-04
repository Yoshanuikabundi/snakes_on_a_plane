"""
Tests for the config module
"""

# Import package, test suite, and other packages as needed
import pytest
import toml
from pathlib import Path

import soap.config as cfg

MAXIMALIST_VALIDATED = {
    "envs": {
        "test": {
            "yml_path": Path("devtools/conda-envs/test_env.yml"),
            "env_path": None,
            "install_current": True,
        },
        "docs": {
            "yml_path": Path("devtools/conda-envs/docs_env.yml"),
            "env_path": None,
            "install_current": False,
        },
        "user": {
            "yml_path": Path("devtools/conda-envs/user_env.yml"),
            "env_path": Path("/home/someone/conda/envs/soap-env"),
            "install_current": True,
        },
    },
    "aliases": {
        "list": {
            "cmd": "conda list",
            "chdir": False,
            "env": "test",
            "description": None,
            "passthrough_args": False,
        },
        "greet": {
            "cmd": "echo hello world",
            "chdir": False,
            "env": "test",
            "description": None,
            "passthrough_args": False,
        },
        "docs": {
            "cmd": "sphinx-build -j auto docs docs/_build/html",
            "chdir": True,
            "env": "docs",
            "description": "Build the docs with Sphinx",
            "passthrough_args": True,
        },
    },
}


def test_maximalist_toml():
    """Check that a maximalist toml file validates correctly."""
    data = toml.load("soap/tests/data/maximalist.toml")
    validated = cfg.CFG_SCHEMA.validate(data)
    assert validated == MAXIMALIST_VALIDATED


def test_maximalist_cfg():
    git_root = Path("/home/someone/project/")
    config = cfg.Config(cfg=MAXIMALIST_VALIDATED, git_root=git_root)
    assert config.envs["test"].env_path == git_root / ".soap/test"
    assert config.envs["docs"].env_path == git_root / ".soap/docs"
    assert config.envs["user"].env_path == Path("/home/someone/conda/envs/soap-env")
