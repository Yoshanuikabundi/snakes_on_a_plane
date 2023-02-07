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
    """
    n_pips = 0
    for entry in dependencies:
        if isinstance(entry, dict) and "pip" in entry:
            n_pips += 1
            entry["pip"].append(package)
    if n_pips == 0:
        dependencies.append({"pip": [package]})


def prepare_env_file(env: Env) -> Dict:
    """
    Prepare an environment file and write it to the returned path

    The environment's name is augmented with a hash of the original file.
    Dependencies are appended to the dependency list, while channels are
    preprended. Returns the name of the written file.
    """
    # Get a hash of the input YAML file
    env_hash = hashlib.md5(env.yml_path.read_bytes()).hexdigest()

    # Read the YAML file in to a dict
    env_dict = yaml.safe_load(env.yml_path.read_text())

    # Update the name, channels and dependencies of the environment
    env_dict["name"] = env_dict.get("name", "") + "." + env_hash
    env_dict["channels"] = env.additional_channels + env_dict.get("channels", [])
    env_dict.setdefault("dependencies", []).extend(env.additional_dependencies)

    # Add the current package if required
    if env.install_current:
        add_pip_package(
            f"-e {env.package_root}",
            env_dict["dependencies"],
        )

    # Choose an output file name
    path_out = env.env_path / ".soap_env-working.yml"

    # Write the updated environment
    path_out.parent.mkdir(exist_ok=True)
    path_out.write_text(yaml.dump(env_dict))

    # Return the output file name
    return path_out


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
    # Prepare the working environment file
    working_yaml_path = prepare_env_file(env)

    # We need a path to cache our prepared environment to after building
    cached_yaml_path = env.env_path / ".soap_env.yml"

    # Create the environment, or clean up what we've already prepared
    if (
        ignore_cache
        or (not cached_yaml_path.exists())
        or (not filecmp.cmp(cached_yaml_path, working_yaml_path))
    ):
        # Create the environment
        soap.conda.env_from_file(
            working_yaml_path,
            env.env_path,
            allow_update=allow_update,
        )
        # Cache the environment file we used
        working_yaml_path.rename(cached_yaml_path)
    else:
        # Nothing to do, so clean up the files we made
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
