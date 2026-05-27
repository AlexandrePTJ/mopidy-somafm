# mopidy-somafm

[![Latest PyPI version](https://img.shields.io/pypi/v/mopidy-somafm)](https://pypi.org/p/mopidy-somafm)
[![CI build status](https://img.shields.io/github/actions/workflow/status/AlexandrePTJ/mopidy-somafm/ci.yml)](https://github.com/AlexandrePTJ/mopidy-somafm/actions/workflows/ci.yml)
[![Test coverage](https://img.shields.io/codecov/c/gh/AlexandrePTJ/mopidy-somafm)](https://codecov.io/gh/AlexandrePTJ/mopidy-somafm)

Mopidy extension for SomaFM


## Installation

Install by running:

```sh
python3 -m pip install mopidy-somafm
```

See https://mopidy.com/ext/somafm/ for alternative installation methods.


## Configuration

Before starting Mopidy, you must add configuration for
mopidy-somafm to your Mopidy configuration file:

```ini
[somafm]
# TODO: Add example of extension config
```


## Project resources

- [Source code](https://github.com/AlexandrePTJ/mopidy-somafm)
- [Issues](https://github.com/AlexandrePTJ/mopidy-somafm/issues)
- [Releases](https://github.com/AlexandrePTJ/mopidy-somafm/releases)


## Development

### Set up development environment

Clone the repo using, e.g. using [gh](https://cli.github.com/):

```sh
gh repo clone AlexandrePTJ/mopidy-somafm
```

Enter the directory, and install dependencies using [uv](https://docs.astral.sh/uv/):

```sh
cd mopidy-somafm/
uv sync
```

### Running tests

To run all tests and linters in isolated environments, use
[tox](https://tox.wiki/):

```sh
tox
```

To only run tests, use [pytest](https://pytest.org/):

```sh
pytest
```

To format the code, use [ruff](https://docs.astral.sh/ruff/):

```sh
ruff format .
```

To check for lints with ruff, run:

```sh
ruff check .
```

To check for type errors, use [pyright](https://microsoft.github.io/pyright/):

```sh
pyright .
```

### Setup before first release

Before the first release, you must [enable trusted publishing on
PyPI](https://docs.pypi.org/trusted-publishers/creating-a-project-through-oidc/)
so that the `release.yml` GitHub Action can create the PyPI project and publish
releases to PyPI.

When following the instructions linked above, use the following values in the
form at PyPI:

- Publisher: GitHub
- PyPI project name: `mopidy-somafm`
- Owner: `AlexandrePTJ`
- Repository name: `mopidy-somafm`
- Workflow name: `release.yml`
- Environment name: `pypi` (must match environment name in `release.yml`)

### Making a release

To make a release to PyPI, go to the project's [GitHub releases
page](https://github.com/AlexandrePTJ/mopidy-somafm/releases)
and click the "Draft a new release" button.

In the "choose a tag" dropdown, select the tag you want to release or create a
new tag, e.g. `v0.1.0`. Add a title, e.g. `v0.1.0`, and a description of the changes.

Decide if the release is a pre-release (alpha, beta, or release candidate) or
should be marked as the latest release, and click "Publish release".

Once the release is created, the `release.yml` GitHub Action will automatically
build and publish the release to
[PyPI](https://pypi.org/project/mopidy-somafm/).


## Credits

- Original author: [Alexandre Petitjean](https://github.com/AlexandrePTJ)
- Current maintainer: [Alexandre Petitjean](https://github.com/AlexandrePTJ)
- [Contributors](https://github.com/AlexandrePTJ/mopidy-somafm/graphs/contributors)
