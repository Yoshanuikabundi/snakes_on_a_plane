import typer
from typer import echo, Argument, Option
from typing import Callable, List

import soap


def callback(func: Callable) -> typer.Typer:
    return typer.Typer(callback=func)


@callback
def main():
    """
    Snakes on a Plane: Cargo for Conda.
    """
    pass


@main.command()
def update():
    """
    Update all environments in pyproject.toml
    """
    cfg = soap.get_cfg()
    for env in cfg["envs"]:
        soap.prepare_env(env, cfg)


@main.command()
def run(
    args: str = Argument(..., help="Command to run in the specified environment"),
    env: str = Option("dev", help="Environment in which to run the command"),
):
    """Run a command in an environment"""
    cfg = soap.get_cfg()
    soap.prepare_env(env, cfg)
    soap.run_in_env(args.split(), env, cfg)


@main.command()
def list(args: List[str]):
    echo(args)


if __name__ == "__main__":
    main()
