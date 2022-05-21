"""Command Line Interface for Snakes on a Plane"""

from typing import Callable, Optional
import os
import shlex

import typer
from typer import Argument, Option, Typer, echo

import soap
from soap.utils import get_git_root


def callback(func: Callable) -> Typer:
    """Decorator to define a Typer with callback"""
    return Typer(callback=func)


def version_callback(version: bool):
    """Callback for the --version switch"""
    if version:
        echo(f"Snakes On A Plane {soap.__version__}")
        raise typer.Exit()


@callback
def app(
    version: bool = Option(
        False,
        "--version",
        is_eager=True,
        help="Show version and exit.",
        callback=version_callback,
    )
):
    """
    Snakes on a Plane: Cargo for Conda.
    """
    pass


def main():
    """Entry point for Snakes on a Plane.

    Generates commands for aliases and catches and simplifies errors."""
    cfg = soap.Config()
    for alias in cfg.aliases:

        @app.command(alias.name, help=alias.description)
        def _(
            env: str = Option(
                alias.default_env, help="Environment in which to run the command"
            ),
            chdir=Option(alias.chdir, hidden=True),
            command=Option(alias.command, hidden=True),
        ):
            if chdir:
                os.chdir(get_git_root("."))
            run(args=command, env=env)

    try:
        app()
    except Exception as err:
        echo("\033[31mError:\u001b[0m")
        raise SystemExit(err)


@app.command()
def update(
    env: Optional[str] = Option(
        None,
        help="Environment to update. If not specified, all environments will be updated.",
    ),
):
    """
    Update Conda environments.
    """
    cfg = soap.Config()
    envs = cfg.envs.values() if env is None else [cfg.envs[env]]
    echo(
        f"\u001b[36mUpdating {len(envs)} environment{'s' if len(envs) != 1 else ''}\u001b[0m"
    )
    for this_env in envs:
        echo(
            f"\n\u001b[36mPreparing environment '{this_env.name}' "
            + f"from '{this_env.yml_path}' "
            + f"in '{this_env.env_path}':\u001b[0m"
        )
        soap.prepare_env(this_env, ignore_cache=True)


@app.command()
def run(
    args: str = Argument(..., help="Command to run in the specified environment"),
    env: str = Option("dev", help="Environment in which to run the command"),
):
    """Run a command in an environment"""
    cfg = soap.Config()
    this_env = cfg.envs[env]
    soap.prepare_env(this_env)
    soap.run_in_env(shlex.split(args), this_env)


if __name__ == "__main__":
    main()
