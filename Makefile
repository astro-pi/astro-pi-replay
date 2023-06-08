#include gmsl


# TODO the release stuff should only be executed on specific branches.

###################
# Unix Dependencies
###################
CAT:=cat
CUT:=cut
FIND:=find
GREP:=grep
RM:=rm
TOUCH:=touch
TEST:=test
TR:=tr

#####################
# Python dependencies
#####################
PYTHON3:=python3
BUILD:=build
PIP:=pip
PRE_COMMIT:=pre-commit
PYTEST:=pytest
TWINE:=twine
VENV:=venv

###################
# Configuration
###################
CURRENT_BRANCH:=(shell $(GIT) rev-parse --abrev-ref HEAD)
DIST:=dist
MAIN_BRANCH:=main
PYFLAGS=
PYPROJECT:=pyproject.toml
REQUIREMENTS_TXT:=requirements-dev.txt
VENV_NAME:=venv
# Dynamic configuration
NAME:=astro_pi_executor
#NAME:=$(shell $(CAT) $(PYPROJECT) | $(TR) '\n' '\a' | $(GREP) -oE '\[project\]Fname = "[a-z_-]+"' | $(CUT) -d" " -f3 | $(TR) -d '""')
VERSION:=0.0.1
#VERSION:=$(shell $(PYTHON3) -c 'import src.$(NAME) as ex; print(ex.__version__)')
VERSION_MAJOR:=$(shell $(PYTHON3) -c '"$VERSION".split(".")[0]')
VERSION_MINOR:=$(shell $(PYTHON3) -c '"$VERSION".split(".")[1]')
VERSION_PATCH:=$(shell $(PYTHON3) -c '"$VERSION".split(".")[2]')
# TODO:
PY_SOURCES=


###################
# Recipes
###################

all:
	@echo "$(NAME) - $(VERSION)"
	@echo "Options"
	@echo "venv - Build and enter the venv"
	@echo "test - Run tests using tox"
	@echo "clean - Delete cached bytecode and remove the venv"

clean:
	$(RM) -rf $(VENV_NAME) $(DIST)
	$(FIND) -iname "*.pyc" -delete
	$(FIND) -iname "*.egg-info" -delete

$(DIST):	$(VENV)
	. $(VENV_NAME)/bin/activate; $(PYTHON3) $(PYFLAGS) -m $(BUILD)

# Used to ensure an environment variable is set
guard-env-var-%:
	@if [ "${${*}}" = "" ]; then \
	  echo "Environment variable $* not set"; \
          exit 1; \
    	fi

guard-git-branch-%:
	@if [ "${${*}}" != $(CURRENT_BRANCH); then \
	  echo "Expecting branch to be $* but was $(CURRENT_BRANCH)"; \
	  exit 1; \
	fi

pre_commit_install: $(VENV_NAME)
	@echo "Installing pre-commit hooks"
	$(PRE_COMMIT) install --install-hooks

pre_commit_run: pre_commit_install
	$(PRE_COMMIT) run --all

release_github:
	# TODO make sure you are on the main branch
	# TODO make sure there are no changes in the staging area
	@echo "Creating semver tags for $(VERSION)
	$(GIT) tag -f v$(VERSION_MAJOR)
	$(GIT) tag -f v$(VERSION_MAJOR).$(VERSION_MINOR)
	$(GIT) tag -f v$(VERSION_MAJOR).$(VERSION_MINOR).$(VERSION_PATCH)
	@echo "Overwriting the remote tags"
	git push -f origin $(MAIN_BRANCH) --tags

release_test_pypi: $(VENV)
	# TODO make sure the API keys are set
	. $(VENV_NAME)/bin/activate
	$(TWINE) check $(DIST)/*
	$(TWINE) upload -r TestPyPi $(DIST)/*

setup_developer: install_git_pre_commit_hooks $(VENV_NAME)
	@echo "Activate venv with $(VENV_NAME)/bin/activate

test: $(VENV_NAME)
	. $(VENV_NAME)/bin/activate; $(PYTEST) -s

$(VENV_NAME)/touchfile: $(REQUIREMENTS_TXT)
	$(TEST) -d $(VENV_NAME) || $(PYTHON3) $(PYFLAGS) -m $(VENV) $(VENV_NAME)
	. $(VENV_NAME)/bin/activate; $(PIP) install -Ur $(REQUIREMENTS_TXT)
	$(TOUCH) $(VENV_NAME)/touchfile

$(VENV_NAME): $(VENV_NAME)/touchfile

foo: guard-env-var-FOO

bar: guard-git-branch-main
