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


@main.command()
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
