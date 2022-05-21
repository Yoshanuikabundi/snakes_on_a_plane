from typing import Sequence
import soap.conda
from soap.config import Env
import shutil
import filecmp


def prepare_env(env: Env, ignore_cache=False):
    path_yml = env.yml_path
    path_env = env.env_path
    # Cache the environment file and only construct the environment if it has changed
    path_cached_yml = path_env / path_yml.name
    if (
        ignore_cache
        or (not path_cached_yml.exists())
        or (not filecmp.cmp(path_cached_yml, path_yml))
    ):
        soap.conda.env_from_file(path_yml, path_env, install_current=True)
        shutil.copy2(path_yml, path_env)


def run_in_env(args: Sequence[str], env: Env):
    soap.conda.run_in_env(args, env.env_path)
