"""Functions for running Conda and Mamba"""

from os import environ
from pathlib import Path
from typing import Sequence, Dict, Optional, Union
from shutil import which, rmtree
import subprocess as sp

__all__ = ["conda", "env_from_file", "run_in_env"]


def conda(
    args: Sequence[str],
    *,
    stdin: Optional[str] = None,
    env: Optional[Dict[str, str]] = None,
    cmd: Optional[str] = None,
):
    """
    Call conda or mamba with the specified arguments

    Parameters
    ==========

    args
        Arguments to pass to conda.
    stdin
        A string to provide as stdin to conda. By default, nothing is passed.
    env
        Environment variables to pass to conda. By default, the calling
        environment is passed.
    cmd
        Path or name of conda or mamba executable. By default, ``"mamba"`` is
        is used if it can be found, otherwise ``"conda"``.

    Raises
    ======

    subprocess.CalledProcessError
        If Conda finishes with a non-zero exit code.

    """
    env = dict(environ) if env is None else env

    if cmd is None:
        if "MAMBA_EXE" in env:
            cmd = env["MAMBA_EXE"]
        elif which("micromamba") is not None:
            cmd = "micromamba"
        elif which("mamba") is not None:
            cmd = "mamba"
        elif "CONDA_EXE" in env:
            cmd = env["CONDA_EXE"]
        elif which("conda") is not None:
            cmd = "conda"
        else:
            raise ValueError("No conda binary found")

    return sp.run([cmd, *args], check=True, text=True, input=stdin, env=env)


def env_from_file(
    file: Union[str, Path],
    env_path: Union[str, Path],
    allow_update: bool = True,
):
    """
    Create or update an enviroment from a Conda environment YAML file

    Parameters
    ==========

    file
        Path to the Conda environment YAML file
    env_path
        Path to the prefix to create or update the Conda environment
    allow_update
        If ``True``, attempt to update an existing environment. If ``False``,
        delete and recreate an existing environment.
    """
    env_path = Path(env_path)

    # Update the environment if allowed, and early return if successful
    if allow_update and env_path.exists():
        try:
            conda(
                [
                    "update",
                    "--file",
                    str(file),
                    "--prefix",
                    str(env_path),
                    "--prune",
                ]
            )
        except sp.CalledProcessError:
            print("Updating environment in place failed; creating new environment.")
        else:
            return

    # Clean up any existing environment directory
    if env_path.exists():
        rmtree(env_path)

    # Create the new environment
    conda(
        [
            "create",
            "--file",
            str(file),
            "--prefix",
            str(env_path),
        ]
    )


def run_in_env(args: Sequence[str], env_path: Union[str, Path]):
    """
    Run a command in the specified environment prefix

    Parameters
    ==========

    args
        The command to run.
    env_path
        The path to the prefix of the environment.
    """
    conda(
        [
            "run",
            f"--prefix={env_path}",
            f"--attach=STDIN",
            f"--attach=STDOUT",
            f"--attach=STDERR",
            *args,
        ]
    )
