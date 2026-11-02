# Coding environment

This page explains how to set up your computer to develop on the RS-Python Python repositories
([rs-server](https://github.com/RS-PYTHON/rs-server), [rs-client-libraries](https://github.com/RS-PYTHON/rs-client-libraries),
[rs-dpr-service](https://github.com/RS-PYTHON/rs-dpr-service), [rs-testmeans](https://github.com/RS-PYTHON/rs-testmeans)...).
It assumes a Linux or macOS computer. No specific IDE is required, [Visual Studio Code](https://code.visualstudio.com/)
and [PyCharm](https://www.jetbrains.com/pycharm/) are both used by the team.

## Prerequisites

| Tool | Usage |
|---|---|
| [git](https://git-scm.com/) | Get the source code. |
| [Docker](https://docs.docker.com/engine/install/) | Run the [local mode](../rs-demo/docs/local-mode.md), build the Docker images. |
| [pyenv](https://github.com/pyenv/pyenv) (recommended) | Install the Python versions used by the project. |
| [pipx](https://pipx.pypa.io/) (recommended) | Install the Python tools in isolated environments. |
| [Poetry](https://python-poetry.org/) | Manage the dependencies and the virtual environments of the projects. |
| [pre-commit](https://pre-commit.com/) | Run the code checks before each commit. |
| [Trivy](https://trivy.dev/) | Security and license checks, run by pre-commit and the CI. |

```shell
# Install the Python version used by the project (see the "python" constraint of each pyproject.toml)
pyenv install 3.13.18
pyenv global 3.13.18

# Install Poetry (use the version of the CI, see the RS-PYTHON/actions repository)
pipx install poetry
```

## Get the source code

Clone the repositories in a common parent folder, e.g.:

```shell
mkdir ~/rspy && cd ~/rspy
for repo in rs-server rs-client-libraries rs-dpr-service rs-demo rs-testmeans rs-documentation; do
  git clone https://github.com/RS-PYTHON/${repo}.git
done
```

The default branch of the repositories is `develop`.

## Set up a project

From each repository:

```shell
cd ~/rspy/rs-server

# Create the virtual environment and install the dependencies, including the development ones
poetry install --with dev

# Install the OpenTelemetry instrumentation of the installed libraries
poetry run opentelemetry-bootstrap -a install

# Install the git hooks
poetry run pre-commit install
```

Configure your IDE to use the Poetry virtual environment (`poetry env info --path`), and to run the formatters
([black](https://black.readthedocs.io/), [isort](https://pycqa.github.io/isort/)) when you save a file.

## Run the tests

The tests are written with [pytest](https://docs.pytest.org/) and categorised with markers:

```shell
poetry run pytest -m unit         # fast unit tests, with mockup servers
poetry run pytest -m integration  # integration tests
```

Tips:

- In rs-client-libraries, the tests start a Prefect test server, which is slow. Instead, start a Prefect server
  from the [local mode](../rs-demo/docs/local-mode.md) with `docker compose up prefect-server -d` and set
  `SKIP_PREFECT_TEST_HARNESS=1`.
- The [local mode](../rs-demo/docs/local-mode.md) runs the whole system on your computer, and allows to test your
  local source code without rebuilding the Docker images.

## Code quality

The checks run by pre-commit and by the CI are described in [Contributing](contributing.md#code-style). Run them on
all the files with:

```shell
poetry run pre-commit run --all-files
```

If pre-commit fails after a dependency update or a git conflict resolution, reinstall it with
`poetry run pre-commit uninstall && poetry run pre-commit install`.

## Develop on the cluster

You can also develop from your [JupyterHub](../services/virtual-environment/jupyterhub.md) session on a cluster:
clone the repositories in your home directory, and add them to the Python path of your notebooks:

```python
import sys
sys.path.insert(0, "/home/rspy/rs-demo/notebooks")
sys.path.insert(0, "/home/rspy/rs-client-libraries")
import rs_client, resources
print(rs_client.__path__, resources.__path__)
```

See [Create a custom flow](../rs-client-libraries/docs/doc/advanced/custom-flow.md) for the development of Prefect
flows.
