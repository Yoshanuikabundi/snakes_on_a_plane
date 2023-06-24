from pathlib import Path
from typing import Dict, List, Sequence, Optional, Union
import hashlib
import soap.conda
from soap.config import Env
import shutil
import filecmp
import yaml


def add_pip_package(
    package: str,
    dependencies: List[Union[str, Dict[str, List[str]]]],
):
    """
    Add package to all existing pip entries, or to a new entry if there are none

    ``dependencies`` should be the ``"dependencies"`` entry of a Conda
    environment YAML file. Conda seems to only install the first set of pip
    dependencies, but we'll add to all in case this behavior changes.
    """
    n_pips = 0
    for entry in dependencies:
        if isinstance(entry, dict) and "pip" in entry:
            n_pips += 1
            if entry["pip"] is None:
                entry["pip"] = []
            entry["pip"].append(package)
    if n_pips == 0:
        dependencies.append({"pip": [package]})


def prepare_env_file(env: Env) -> str:
    """
    Prepare an environment YAML file and return its contents

    The environment's name is augmented with a hash of the original file.
    Dependencies are appended to the dependency list, while channels are
    preprended. If ``install_current`` is set, it is added to the list of
    installed pip packages.
    """
    # Get a hash of the input YAML file
    env_hash = hashlib.md5(env.yml_path.read_bytes()).hexdigest()

    # Read the YAML file in to a dict
    env_dict = yaml.safe_load(env.yml_path.read_text())

    # Update the name, channels and dependencies of the environment
    env_dict["name"] = env_dict.get("name", "") + "." + env_hash
    env_dict["channels"] = env.additional_channels + env_dict.get("channels", [])
    env_dict.setdefault("dependencies", []).extend(env.additional_dependencies)

    # Add the current package, in dev mode, if required
    if env.install_current:
        add_pip_package(
            f"-e {env.package_root}[all]",
            env_dict["dependencies"],
        )

    return yaml.dump(env_dict, indent=4)


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
        If ``True``, rebuild or update the environment even if the cache
        suggests it is up-to-date. If ``False``, only rebuild or update the
        environment when the YAML file or additional dependencies and channels
        has changed since the last build.
    allow_update
        If ``True``, attempt to update an existing environment. If ``False``,
        delete and recreate an existing environment.
    """
    # Create the parent destination directory if it does not exist
    env.env_path.parent.mkdir(parents=True, exist_ok=True)

    # Prepare the working environment file
    # This file has all the changes we have made to the source YAML file.
    # We can't store this in the nascent environment directory because
    # micromamba will complain; however, this file will get cleaned up by the
    # end of the function so it's ok to put it in the parent.
    working_yaml_path = (
        env.env_path.parent / f".soap_env-working-{env.env_path.name}.yml"
    )
    working_yaml_path.write_text(prepare_env_file(env))

    # We need a path to cache our prepared environment YAML to after building,
    # so that next time we can skip environment creation if nothing's changed.
    # This CAN go in the environment directory.
    cached_yaml_path = env.env_path / ".soap_env.yml"

    # Create or update the environment, or clean up the above if we hit the
    # cache
    if (
        ignore_cache
        or (not env.env_path.exists())
        or (not cached_yaml_path.exists())
        or (not filecmp.cmp(cached_yaml_path, working_yaml_path))
    ):
        # Create or update the environment
        soap.conda.env_from_file(
            working_yaml_path,
            env.env_path,
            allow_update=allow_update,
        )
        # Cache the environment file we used
        working_yaml_path.rename(cached_yaml_path)
    else:
        # Cache hit - environment spec hasn't changed since last time.
        # Nothing to do, so clean up the files we made.
        # If the earlier ``mkdir()`` created a new folder, then we definitely
        # didn't hit the cache, so we don't need to clean it up.
        working_yaml_path.unlink()


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
