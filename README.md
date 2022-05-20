Snakes on a Plane
=================
[//]: # (Badges)
[![GitHub Actions Build Status](https://github.com/yoshanuikabundi/snakes_on_a_plane/workflows/CI/badge.svg)](https://github.com/yoshanuikabundi/snakes_on_a_plane/actions?query=workflow%3ACI)
[![codecov](https://codecov.io/gh/yoshanuikabundi/snakes_on_a_plane/branch/main/graph/badge.svg)](https://codecov.io/gh/yoshanuikabundi/snakes_on_a_plane/branch/main)

[Conda] meets [Cargo]. SOAP lets you easily maintain Conda environments for individual projects.

Specify environments in `soap.toml`:

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
 
[Conda]: https://conda.io
[Cargo]: https://doc.rust-lang.org/cargo/

### Copyright

Copyright (c) 2021, Josh Mitchell (Yoshanuikabundi)


#### Acknowledgements
 
Project based on the 
[Computational Molecular Science Python Cookiecutter](https://github.com/molssi/cookiecutter-cms) version 1.6.
