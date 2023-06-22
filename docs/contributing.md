# Contributing

This page includes information helpful to prospective and current contributors to `astro_pi_executor`.

## Licence

All contributors to `astro_pi_executor` agree with the terms of the [licence](./LICENCE).

## Creating a developer environment

Since this is a pure Python project it is very easy to set up a basic developer environment:

1. Install [Python](https://www.python.org/) (see [pyproject.toml](./pyproject.toml) for up to date Python version requirements).
2. Set up a [venv](https://docs.python.org/3/library/venv.html) with `python3 -m venv venv`
3. Activate the venv with `source venv/bin/activate`.
4. Install the dev dependencies with `pip install -r requirements-dev.txt`
5. Install the [pre-commit](https://pre-commit.com/) hooks with `pre-commit install --install-hooks`

Having followed these instructions you should be inside a venv that has all the dependencies available, and before you commit any changes a series of pre-commit checks will be made to ensure good code quality.

## Workflow

This project uses a [trunk-based development workflow](https://www.atlassian.com/continuous-delivery/continuous-integration/trunk-based-development). This means that there is one branch called `main` which _all_ PRs are based off and merged to. Merging to `main` will kick off a series of tests that, if no problems are found, will result in a new release being automatically deployed to TestPyPi, PyPi, and Github Packages, and the Astro Pi PPA.

## CI / CD

The `astro_pi_executor` repository uses Github Actions for its Continuous Integration (CI) and Continuous Delivery (CD) pipelines. However, so as to not be 'locked-in' to Github Actions permanently and to more easily debug any issues that occur during a particular CI and CD pipeline - all pipelines primarly make use of standard Unix tools (including [GNUmake](https://www.gnu.org/software/make/)).

Contributors therefore may wish to have access to a Unix-like environment, in order to replicate any issues encountered in the CI/CD processes - Windows users may use [mingw-w64](https://www.gnu.org/software/make/) or [WSL](https://learn.microsoft.com/en-us/windows/wsl/install).

For diagnosing any issues with the Docker builds - naturally it is required to have [Docker](https://www.docker.com/) installed.

## Issues / Bug Tracker

Open issues are listed in the [Github issue tracker](https://github.com/astro-pi/astro_pi_executor).

