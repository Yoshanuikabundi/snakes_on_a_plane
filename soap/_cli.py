"""Command Line Interface for Snakes on a Plane"""

from typing import Callable, Optional
import os
import shlex
from subprocess import CalledProcessError

import typer
from typer import Argument, Option, Typer
import rich, rich.tree

import soap
from soap.config import DEFAULT_ENV

NO_SUBCOMMAND_EXIT_CODE = 1
"""Exit code given when no subcommand is provided at command line"""

CONSOLE = rich.console.Console()


def callback(func: Callable) -> Typer:
    """Decorator to define a Typer with callback"""
    return Typer(
        callback=func,
        invoke_without_command=True,
        rich_markup_mode="rich",
    )


@callback
def app(
    ctx: typer.Context,
    version: bool = Option(
        False,
        "--version",
        is_eager=True,
        help="Show version and exit.",
    ),
):
    """
    Snakes on a Plane: Cargo for Conda.
    """
    if version:
        CONSOLE.print(f"Snakes On A Plane {soap.__version__}")
        raise typer.Exit()
    if ctx.invoked_subcommand is None:
        CONSOLE.print("No subcommand given; for help, pass '--help'")
        raise typer.Exit(NO_SUBCOMMAND_EXIT_CODE)


def main():
    """Entry point for Snakes on a Plane.

    Generates commands for aliases and catches and simplifies errors."""
    cfg = soap.Config()
    for alias in cfg.aliases:

        @app.command(
            alias.name,
            help=alias.description,
            context_settings={
                "allow_extra_args": alias.passthrough_args,
                "ignore_unknown_options": alias.passthrough_args,
            },
            rich_help_panel="Aliases",
        )
        def _(
            ctx: typer.Context,
            env: str = Option(
                alias.default_env,
                help="Environment in which to run the command",
            ),
            chdir: Optional[str] = Option(
                None if alias.chdir is None else str(alias.chdir),
                hidden=True,
            ),
            command: str = Option(
                alias.command,
                hidden=True,
            ),
            passthrough_args: bool = Option(
                alias.passthrough_args,
                hidden=True,
            ),
        ):
            if chdir:
                os.chdir(chdir)
            if passthrough_args:
                command = " ".join([command, *ctx.args])
            run(args=command, env=env)

    try:
        app()
    except Exception as err:
        CONSOLE.print("[red]Error:")
        if os.environ.get("SOAP_DEBUG", ""):
            raise err
        else:
            raise SystemExit(err)


@app.command()
def update(
    env: Optional[str] = Option(
        None,
        help="Environment to update. If not specified, all environments will be updated.",
    ),
    recreate: bool = Option(
        False,
        help="Delete and recreate the environment(s), rather than attempting to update in place",
    ),
):
    """
    Update Conda environments.
    """
    cfg = soap.Config()
    envs = cfg.envs.values() if env is None else [cfg.envs[env]]
    CONSOLE.print(
        f"[cyan]Updating {len(envs)} environment{'s' if len(envs) != 1 else ''}"
    )
    for this_env in envs:
        CONSOLE.print(
            f"[cyan]Preparing environment '{this_env.name}' "
            + f"from '{this_env.yml_path}' "
            + f"in '{this_env.env_path}'"
        )
        soap.prepare_env(
            this_env,
            ignore_cache=True,
            allow_update=not recreate,
        )


@app.command()
def run(
    args: str = Argument(..., help="Command to run in the specified environment"),
    env: str = Option(DEFAULT_ENV, help="Environment in which to run the command"),
):
    """Run a command in an environment."""
    cfg = soap.Config()
    this_env = cfg.envs[env]
    soap.prepare_env(this_env)
    try:
        soap.run_in_env(shlex.split(args), this_env)
    except CalledProcessError as e:
        exit(e.returncode)


@app.command()
def list(
    verbosity: int = typer.Option(
        0,
        "--verbose",
        "-v",
        count=True,
        help="Present more information.",
    )
):
    """List the available environments."""
    cfg = soap.Config()

    if verbosity < 3:
        captions = [
            "📦 Is the root package installed in this environment?",
            "🪧 Number of additional channels\n📥 Number of additional dependencies",
        ]

        table = rich.table.Table(
            title="Snakes on a Plane environments",
            caption="\n" + "\n".join(captions[:verbosity]),
            caption_justify="left",
            caption_style="dim",
            box=rich.box.SIMPLE,
            show_edge=False,
        )

        table.add_column("Name", style="bold")
        table.add_column("YML path")
        if verbosity > 0:
            table.add_column("📦")
        if verbosity > 1:
            table.add_column("🪧")
            table.add_column("📥")

        for env in cfg.envs.values():
            row = [env.name, str(env.yml_path)]
            if verbosity > 0:
                row.append("✓" if env.install_current else "")
            if verbosity > 1:
                row.append(str(len(env.additional_channels)))
                row.append(str(len(env.additional_dependencies)))

            table.add_row(*row)

        CONSOLE.print(table)
    else:
        tree = rich.tree.Tree("[i]Snakes on a Plane environments", guide_style="dim")

        for env in cfg.envs.values():
            branch = tree.add(f"[cyan bold]{env.name}")
            yml_branch = branch.add(f"[b]YAML path:[/b] {env.yml_path}")
            branch.add(f"[b]Environment path:[/b] {env.env_path}")
            environment_exists = (
                "Yes" if (env.env_path / "conda-meta").exists() else "No"
            )
            branch.add(f"[b]Environment exists?:[/b] {environment_exists}")
            branch.add(f"[b]Install root package:[/b] {env.install_current}")
            if env.additional_channels or verbosity > 3:
                branch.add(f"[b]Additional channels:[/b] {env.additional_channels}")
            if env.additional_dependencies or verbosity > 3:
                branch.add(
                    f"[b]Additional dependencies:[/b] {env.additional_dependencies}"
                )
            if verbosity > 3:
                syntax = rich.syntax.Syntax(env.yml_path.read_text(), "yaml")
                yml_branch.add(syntax)
            if verbosity > 4:
                branch.add(
                    f"[b]Command to update environment:[/b] [u]soap update --env {env.name}"
                )
                branch.add(
                    f"[b]Command to recreate environment:[/b] [u]soap update --recreate --env {env.name}"
                )

        CONSOLE.print(tree)


_click = typer.main.get_command(app)

if __name__ == "__main__":
    main()
