from typing import Callable, Mapping
import os

import typer
from typer import Argument, Option, Typer, echo

import soap
from soap.utils import get_git_root


def callback(func: Callable) -> Typer:
    return Typer(callback=func)


def version_callback(version: bool):
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
    cfg = soap.get_cfg()
    for alias, inner in cfg["aliases"].items():
        if isinstance(inner, str):
            inner = {"cmd": inner}
        command = inner["cmd"]
        chdir = inner.get("chdir", False)
        default_env = inner.get("env", "dev")
        description = inner.get("description", None)

        @app.command(alias, help=description)
        def _(
            env: str = Option(
                default_env, help="Environment in which to run the command"
            )
        ):
            if chdir:
                os.chdir(get_git_root("."))
            run(args=command, env=env)

    try:
        app()
    except Exception as err:
        echo("\033[31mError:")
        raise SystemExit(err)


@app.command()
def update(
    env: str = Option(
        ...,
        help="Environment to update. If not specified, all environments will be updated.",
    ),
):
    """
    Update all environments in soap.toml
    """
    cfg = soap.get_cfg()
    if env is not None:
        soap.prepare_env(env, cfg, ignore_cache=True)
    else:
        for env in cfg["envs"]:
            soap.prepare_env(env, cfg, ignore_cache=True)


@app.command()
def run(
    args: str = Argument(..., help="Command to run in the specified environment"),
    env: str = Option("dev", help="Environment in which to run the command"),
):
    """Run a command in an environment"""
    cfg = soap.get_cfg()
    soap.prepare_env(env, cfg)
    soap.run_in_env(args.split(), env, cfg)


if __name__ == "__main__":
    main()
