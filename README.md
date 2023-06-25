# Snakes on a Plane

[//]: # (Badges)
[![GitHub Actions Build Status](https://github.com/yoshanuikabundi/snakes_on_a_plane/workflows/CI/badge.svg)](https://github.com/yoshanuikabundi/snakes_on_a_plane/actions?query=workflow%3ACI)
[![codecov](https://codecov.io/gh/yoshanuikabundi/snakes_on_a_plane/branch/main/graph/badge.svg)](https://codecov.io/gh/yoshanuikabundi/snakes_on_a_plane/branch/main)
[![Documentation Status](https://readthedocs.org/projects/snakesonaplane/badge/?version=latest)](https://snakesonaplane.readthedocs.io/en/latest/?badge=latest)

[Conda] meets [Cargo]. SOAP lets you easily maintain Conda environments for individual projects.

Soap is configured in `soap.toml`. SOAP always looks for this file in the root of the git repository it was called from. It can also be configured in the `tool.soap` table of `pyproject.toml`. Specify environments with a name and a Conda environment YAML file:

```toml
[envs]
dev = "devtools/conda-envs/test_env.yml"
user = "devtools/conda-envs/user_env.yml"
docs = "devtools/conda-envs/docs_env.yml"
```

Then run commands in an environment with `soap run`:

```shell
soap run --env docs "sphinx-build -n auto docs docs/_build/html"
```

SOAP will check that the environment matches the specification with every call, so if you pull in an update to `docs_env.yml` and run `soap run ...` again, your environment will be updated. This won't necessarily update dependencies if the spec hasn't changed; to do this, run `soap update`:

```shell
soap update
```

You can also define your own aliases for commands. For simple commands, define the command as a value in the `aliases` table:

```toml
[aliases]
greet = "echo 'hello world'"
```

To configure an alias, define a table instead of a string:

```toml
[aliases.docs]
cmd = "sphinx-build -j auto docs docs/_build/html"
chdir = true # Run the command in the git repository root directory
env = "docs" # Use the docs environment by default
description = "Build the docs with Sphinx" # Description for --help
```

In either case, the alias becomes a sub-command:

```shell
soap greet
```

The environment used by an alias can be defined in the TOML file, but it can also be overridden on the command line:

```shell
soap docs --env user
```

SOAP will always check that the environment is correct before running aliases, just like for `soap run`!
 
[Conda]: https://conda.io
[Cargo]: https://doc.rust-lang.org/cargo/

## Installation

I recommend installing [`pipx`] and [`micromamba`] with your system package manager, and then installing SOAP with `pipx`. This will give you a fast, easy to manage Conda installation and will avoid installing anything in your system Python distribution. For example, with the Paru package manager for Arch Linux:

```shell
paru -Syu python-pipx micromamba-bin
git clone https://github.com/Yoshanuikabundi/snakes_on_a_plane.git
cd snakes_on_a_plane
pipx install .
```

If you have an existing Mamba or Conda installation, SOAP should be able to detect and use it - just install `pipx` and SOAP.

If you're using Conda, I highly recommend Mamba - it's much faster than Conda, can solve environments that Conda can't, and has an identical API. Install it with:

```shell
conda install -n base mamba
```

[`pipx`]: https://pypa.github.io/pipx/
[`micromamba`]: https://mamba.readthedocs.io/en/latest/user_guide/micromamba.html

## Copyright

Copyright (c) 2021, Josh Mitchell (Yoshanuikabundi)


## Acknowledgements
 
Project based on the [Computational Molecular Science Python Cookiecutter](https://github.com/molssi/cookiecutter-cms) version 1.6.
