from typing import Sequence
import soap.conda
from soap.config import Env
import shutil
import filecmp


def prepare_env(env: Env, ignore_cache=False):
    """
    Prepare the provided environment

    Parameters
    ==========

    env
        The environment to prepare
    ignore_cache
        If True, rebuild the environment even if the cache suggests it is
        up-to-date. If False, only rebuild the environment when the YAML file
        itself has changed since the last build.
    """
    path_yml = env.yml_path
    path_env = env.env_path
    # Cache the environment file and only construct the environment if it has changed
    path_cached_yml = path_env / path_yml.name
    if (
        ignore_cache
        or (not path_cached_yml.exists())
        or (not filecmp.cmp(path_cached_yml, path_yml))
    ):
        soap.conda.env_from_file(
            path_yml, path_env, install_current=env.install_current
        )
        shutil.copy2(path_yml, path_env)


def run_in_env(args: Sequence[str], env: Env):
    """
    Run a command in the provided environment. Does not update the environment.

    This function will raise an exception if the provided environment has not
    been prepared. To update the environment and ensure it exists, first call
    ``prepare_env``.

    Parameters
    ==========

    args
        The command to run.
    env
        The environment to run the command in.
    """
    soap.conda.run_in_env(args, env.env_path)
