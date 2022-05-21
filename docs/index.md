Snakes on a Plane
=================

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


:::{toctree}
---
hidden: true
---

Overview <self>
:::

:::{toctree}
---
caption: CLI Reference
hidden: true
---

cli.md
:::

<!-- 
:::{toctree}
---
hidden: true
caption: User Guide
---

::: 
-->

<!--
The autosummary directive renders to rST,
so we must use eval-rst here
-->
:::{eval-rst}
.. raw:: html

    <div style="display: None">

.. autosummary::
   :recursive:
   :caption: API Reference
   :toctree: api/generated
   :nosignatures:

   soap

.. raw:: html

    </div>
:::
