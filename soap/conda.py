from os import environ
from pathlib import Path
from typing import Sequence, Dict, Optional, Union
from shutil import which
from subprocess import run
from soap.utils import get_git_root


def conda(
    args: Sequence[str],
    *,
    stdin: Optional[str] = None,
    env: Optional[Dict[str, str]] = None,
    cmd: Optional[str] = None
):
    """Call conda or mamba with the specified arguments

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
        if which("mamba") is not None:
            cmd = "mamba"
            env["MAMBA_NO_BANNER"] = "1"
        else:
            cmd = "conda"
    return run([cmd, *args], check=True, text=True, input=stdin, env=env)


def env_from_file(
    file: Union[str, Path], env_path: Union[str, Path], install_current=False
):
    if Path(env_path).exists():
        conda(
            [
                "env",
                "update",
                "--file",
                str(file),
                "--prefix",
                str(env_path),
                "--prune",
            ]
        )
    else:
        conda(
            [
                "env",
                "create",
                "--file",
                str(file),
                "--prefix",
                str(env_path),
            ]
        )

    if install_current:
        run_in_env(
            [
                "pip",
                "install",
                "-e",
                str(get_git_root(".")),
            ],
            env_path,
        )


def run_in_env(args: Sequence[str], env_path: Union[str, Path]):
    conda(
        [
            "run",
            "--prefix",
            str(env_path),
            "--no-capture-output",
            *args,
        ]
    )
