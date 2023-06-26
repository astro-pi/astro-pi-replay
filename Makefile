##################
# OS Dependencies
##################
CAT:=cat
CUT:=cut
DOCKER:=docker
FIND:=find
GH:=gh
GIT:=git
GREP:=grep
PIP:=pip
PYTHON3:=python3
RM:=rm
SED:=sed
SORT:=sort
TOUCH:=touch
TEST:=test
TR:=tr
XARGS:=xargs

#####################
# Python dependencies
#####################
BUILD:=build
MKDOCS:=mkdocs
VENV_PIP:=pip
PRE_COMMIT:=pre-commit
PYTEST:=pytest
TWINE:=twine
VENV:=venv

###################
# Configuration
###################
CURRENT_BRANCH:=$(shell $(GIT) rev-parse --abbrev-ref HEAD)
DOC_DIR:=docs
DIST_DIR:=dist
GITHUB_NAMESPACE:=astro-pi
GITHUB_CONTAINER_REGISTRY_URL:=ghcr.io

GREP_REGEX_ENGINE:=$(shell $(GREP) "-P" Makefile &> /dev/null && echo "P" || echo "E")
MAIN_BRANCH:=main
# NAME:=astro_pi_executor
PYFLAGS=
PYPROJECT:=pyproject.toml
ifdef PYTEST_DEBUG
PYTEST_FLAGS:=-s --log-cli-level=DEBUG
else
PYTEST_FLAGS:=-s
endif
REQUIREMENTS_TXT:=requirements.txt
SITE_DIR:=site
SRC_DIR:=src
VENV_NAME:=venv
# Dynamic configuration to ensure pyproject.toml is the source of truth
NAME:=$(shell cat $(PYPROJECT) | \
     $(TR) '\n' '\a' | \
     $(GREP) -o$(GREP_REGEX_ENGINE) '\[project\]\aname = "[a-z_-]+"' | \
     $(CUT) -d" " -f3 | \
     $(TR) -d '""')
VERSION:=$(shell $(PYTHON3) -c 'import $(SRC_DIR).$(NAME) as ex; print(ex.__version__)')
VERSION_MAJOR:=$(shell $(PYTHON3) -c 'print("$(VERSION)".split(".")[0])')
VERSION_MINOR:=$(shell $(PYTHON3) -c 'print("$(VERSION)".split(".")[1])')
VERSION_PATCH:=$(shell $(PYTHON3) -c 'print("$(VERSION)".split(".")[2])')
PYTHON_VERSION_EXPR:= $(shell $(CAT) $(PYPROJECT) | \
	$(GREP) "requires-python" | \
	$(CUT) -d" " -f 3)
# the below is a bit brittle, but unlikely to need anything else.
PYTHON_VERSION:=$(shell echo $(PYTHON_VERSION_EXPR) | $(SED) 's/[>="]//g')
GIT_HASH:=$(shell $(GIT) rev-parse --verify HEAD)
DOCKER_IMAGE_NAME:=$(NAME)
DOCKER_IMAGE_TAG:=$(VERSION)_$(GIT_HASH)
PY_SOURCES:=$(shell $(FIND) $(SRC_DIR) -name "*.py")
DOC_SOURCES:=$(shell $(FIND) $(DOC_DIR) -type f)


###################
# Rules
###################

all:
	@echo "(GNU)make targets:"
	@echo ""
	@echo "analyse           - Run static analysis on the codebase."
	@echo "build_docker      - Build the $(DOCKER_IMAGE_NAME) Docker image"
	@echo "build_docs        - Build the mkdocs site"
	@echo "build_python      - Build the python package"
	@echo "build             - Build the Python package, Docker image, and mkdocs site"
	@echo "clean             - Clean (delete files) from the environment"
	@echo "                    and start afresh."
	@echo "diagnostics       - Run diagnostics in case of any problems with"
	@echo "                    this Makefile."
	@echo "install           - Install the Python package into the OS user environment"
	@echo "python_version    - Print the detected minimum Python version"
	@echo "publish_git_tags  - Publish and overwrite git tags to the remote."
	@echo "publish_prod_pypi - Build and publish a release to prod PyPi."
	@echo "publish_test_pypi - Build and publish a release to test PyPi."
	@echo "setup_developer   - Install pre-commit hooks and venv to"
	@echo "                    the developer environment."
	@echo "test              - Run all tests using pytest."
	@echo "uninstall         - Uninstall the Python package from the OS user environment"
	@echo "version           - Print the package version"
	@echo ""

analyse: pre_commit_run


assert_env_var_set_%:
	@if [ "${${*}}" = "" ]; then \
	  echo "Environment variable $* not set"; \
          exit 1; \
    	fi

assert_installed_%:
	@command -v $* || echo "$* not installed"; exit 1

assert_min_python_version_detected:
	@if [ -z $(shell echo '$(PYTHON_VERSION_EXPR)' | \
		$(SED) -E 's/(>=?3\.([0-9]\.){1,2})/\1/g') ]; then \
	  echo "Cannot find minimum version"; \
	  exit 1; \
	fi

assert_on_git_branch_head_or_%:
	@if [ $(CURRENT_BRANCH) != "HEAD" ] && [ "$*" != "$(CURRENT_BRANCH)" ]; then \
	  echo "Expected branch to be $* but was '$(CURRENT_BRANCH)'"; \
	  exit 1; \
	fi

build: build_python build_docs build_docker

build_docker: assert_env_var_set_PYTHON_VERSION
	$(DOCKER) build \
	  --build-arg NAME="$(NAME)" \
	  --build-arg BIN_NAME="$(NAME)" \
	  --build-arg PYTHON_VERSION="$(PYTHON_VERSION)" \
	  --build-arg VENV_NAME="$(VENV_NAME)" \
	  -t $(DOCKER_IMAGE_NAME):$(DOCKER_IMAGE_TAG) .

build_docs: $(VENV) $(DOC_SOURCES)
	. $(VENV_NAME)/bin/activate; $(MKDOCS) build

build_python: $(DIST_DIR)

clean:
	@$(RM) -rf $(VENV_NAME) $(DIST_DIR) $(SITE_DIR)
	@$(FIND) . -iname "__pycache__" | $(SORT) -r | $(XARGS) -I{} rm -rf {}
	@$(FIND) . -iname "*.pyc" | $(SORT) -r | $(XARGS) -I{} rm -f {}
	@$(FIND) . -iname "*.egg-info" | $(SORT) -r | $(XARGS) -I{} rm -rf {}
	@$(eval DOCKER_IMG_ID:=$(shell docker images --filter=reference="*$(NAME):*" -q))
	@if [ -n "$(DOCKER_IMG_ID)" ]; then \
	  $(DOCKER) rmi $(DOCKER_IMG_ID); \
	fi

diagnostics:
	@echo "Detected project name: $(NAME)"
	@echo "Detected version is: $(VERSION)"
	@echo "Detected major version is: $(VERSION_MAJOR)"
	@echo "Detected minor version is: $(VERSION_MINOR)"
	@echo "Detected patch version is: $(VERSION_PATCH)"

$(DIST_DIR):	$(VENV)
	. $(VENV_NAME)/bin/activate; $(PYTHON3) $(PYFLAGS) -m $(BUILD)

install: build_python
	$(PIP) install --user $(DIST_DIR)/*.whl

pre_commit_install: $(VENV_NAME)
	@echo "Installing pre-commit hooks"
	. $(VENV_NAME)/bin/activate; \
	$(PRE_COMMIT) install --install-hooks

pre_commit_run: pre_commit_install
	$(PRE_COMMIT) run --all

python_version: assert_min_python_version_detected
	@echo $(PYTHON_VERSION)

publish_docs: assert_on_git_branch_head_or_main build_docs
	@echo "Deploying docs to Github"
	$(MKDOCS) gh-deploy

publish_docker: assert_on_git_branch_head_or_main assert_env_var_set_GITHUB_TOKEN build_docker publish_git_tags
	@echo "Publishing Docker image"
	$(DOCKER) login $(GITHUB_CONTAINER_REGISTRY_URL) -u USERNAME --password-stdin
	$(DOCKER) push $(GITHUB_CONTAINER_REGISTRY_URL)/$(GITHUB_NAMESPACE)/$(DOCKER_IMAGE_NAME):$(DOCKER_IMAGE_TAG)
	$(DOCKER) tag $(DOCKER_IMAGE_NAME):$(DOCKER_IMAGE_TAG) $(DOCKER_IMAGE_NAME):latest
	$(DOCKER) push $(GITHUB_CONTAINER_REGISTRY_URL)/$(GITHUB_NAMESPACE)/$(DOCKER_IMAGE_NAME):latest

publish_github_release: assert_on_git_branch_head_or_main publish_git_tags $(DIST)
	$(GH) release create --generate-notes v$(VERSION_MAJOR).$(VERSION_MINOR).$(VERSION_PATCH) $(DIST)/*

publish_git_tags: assert_on_git_branch_head_or_main
	@echo "Creating semver tags for $(VERSION)"
	$(GIT) tag -f $(VERSION_MAJOR)
	$(GIT) tag -f $(VERSION_MAJOR).$(VERSION_MINOR)
	$(GIT) tag -f $(VERSION_MAJOR).$(VERSION_MINOR).$(VERSION_PATCH)
	@echo "Overwriting the remote tags"
	$(GIT) push -f origin --tags

publish_test_pypi: assert_on_git_branch_head_or_main assert_env_var_set_TWINE_USERNAME \
	assert_env_var_set_TWINE_PASSWORD $(VENV)
	. $(VENV_NAME)/bin/activate; \
	$(TWINE) check $(DIST_DIR)/* ; \
	$(TWINE) upload -r TestPyPi $(DIST_DIR)/*

publish_prod_pypi: assert_on_git_branch_head_or_main assert_env_var_set_TWINE_USERNAME \
	assert_env_var_set_TWINE_PASSWORD $(VENV)
	. $(VENV_NAME)/bin/activate; \
	$(TWINE) check $(DIST_DIR)/* ; \
	$(TWINE) upload $(DIST_DIR)/*

setup_developer: $(VENV_NAME) pre_commit_install
	@echo "Activate venv with $(VENV_NAME)/bin/activate"
	@echo "or use direnv"

test: $(VENV_NAME)
	. $(VENV_NAME)/bin/activate; $(PYTEST) $(PYTEST_FLAGS)

test_smoke_%:
	@echo "Running smoke tests on env $*"
	$(eval TMP:=$(shell mktemp -d))
	cd $(TMP)
	python3 -m venv venv ; \
	. source venv/bin/activate ; \
	pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ your-package ; \
	$(NAME) --help

uninstall:
	$(PIP) uninstall --user $(NAME)

$(VENV_NAME)/touchfile: $(REQUIREMENTS_TXT)
	$(TEST) -d $(VENV_NAME) || $(PYTHON3) $(PYFLAGS) -m $(VENV) $(VENV_NAME) && \
	. $(VENV_NAME)/bin/activate ; \
	$(VENV_PIP) install --upgrade -r $(REQUIREMENTS_TXT) ; \
	$(VENV_PIP) install --editable . ; \
	$(TOUCH) $(VENV_NAME)/touchfile

$(VENV_NAME): $(VENV_NAME)/touchfile

version:
	@echo $(VERSION)

.PHONY: all analyse assert_env_var_set_% assert_installed_% assert_min_python_version_detected assert_on_git_branch_head_or_% build build_docker build_docs build_python clean diagnostics install pre_commit_install pre_commit_run python_version publish_docs publish_git_tags publish_test_pypi publish_prod_pypi setup_developer test uninstall version

