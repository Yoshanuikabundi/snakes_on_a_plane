from pathlib import Path
from typing import Dict, List, Sequence, Optional
import hashlib
import soap.conda
from soap.config import Env
import shutil
import filecmp
import yaml


def env_dict_with(
    env_file: Path,
    channels: Optional[List[str]] = None,
    dependencies: Optional[List[str]] = None,
) -> Dict:
    """
    Return a dict encoding the environment file updated with channels or deps.

    The environment's name is augmented with a hash of the original file.
    Dependencies are appended to the dependency list, while channels are
    preprended.
    """
    env_dict = yaml.safe_load(env_file.read_text())
    env_hash = hashlib.md5(env_file.read_bytes()).hexdigest()
    env_dict["name"] = env_dict.get("name", "") + "." + env_hash

    env_dict["channels"] = (channels or []) + env_dict.get("channels", [])
    env_dict.setdefault("dependencies", []).extend(dependencies or [])

    return env_dict


def prepare_env(
    env: Env,
    ignore_cache: bool = False,
    allow_update: bool = True,
):
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
    allow_update
        If ``True``, attempt to update an existing environment. If ``False``,
        delete and recreate an existing environment.
    """
    path_yml = env.yml_path
    path_env = env.env_path
    # Write the environment file we're going to install
    env_dict = env_dict_with(
        path_yml,
        dependencies=env.additional_dependencies,
        channels=env.additional_channels,
    )
    path_working_yml = path_env / ".soap_env-working.yml"
    path_working_yml.write_text(yaml.dump(env_dict))
    # Cache the environment file and only construct the environment if it has
    # changed
    path_cached_yml = path_env / ".soap_env.yml"
    if (
        ignore_cache
        or (not path_cached_yml.exists())
        or (not filecmp.cmp(path_cached_yml, path_working_yml))
    ):
        # Create the environment
        soap.conda.env_from_file(
            path_working_yml,
            path_env,
            install_current=env.install_current,
            allow_update=allow_update,
        )
        # Cache the environment file we used
        path_working_yml.rename(path_cached_yml)
    else:
        # Clean up
        path_working_yml.unlink()


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
