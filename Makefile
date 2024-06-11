#################################################################################
#
# Makefile to build the project
#
#################################################################################

PROJECT_NAME = streaming-data-project
PYTHON_INTERPRETER = python3
WD=$(shell pwd)
PYTHONPATH=${WD}
SHELL := /bin/bash
PIP:=pip

## Create python interpreter environment.
create-environment:
	@echo ">>> About to create environment: $(PROJECT_NAME)..."
	@echo ">>> check python3 version"
	( \
		$(PYTHON_INTERPRETER) --version; \
	)
	@echo ">>> Setting up VirtualEnv."
	( \
	    $(PIP) install -q virtualenv virtualenvwrapper; \
	    virtualenv venv --python=$(PYTHON_INTERPRETER); \
	)

# Define utility variable to help calling Python from the virtual environment
ifeq ($(shell uname),Linux)
    # Linux platform
    ACTIVATE_ENV := source venv/bin/activate
else ifeq ($(shell uname),Darwin)
    # macOS platform
    ACTIVATE_ENV := source venv/bin/activate
else ifeq ($(shell uname),BSD)
    # BSD platform
    ACTIVATE_ENV := source venv/bin/activate
else
    # Default for other platforms
    ACTIVATE_ENV := venv\Scripts\activate
endif


# Execute python related functionalities from within the project's environment
define execute_in_env
	$(ACTIVATE_ENV) && $1
endef

################################################################################################################
# Set Up

## Install project dependencies
install-dependencies:
	$(call execute_in_env, $(PIP) install -r requirements.txt)

## Install flake8
flake:
	$(call execute_in_env, $(PIP) install flake8)

## Install pytest
pytest:
	$(call execute_in_env, $(PIP) install pytest)

## Run the flake8 code check
run-flake:
	$(call execute_in_env, flake8 ./src ./tests)

# Run pep8
run-format:
	$(call execute_in_env, autopep8 --in-place --aggressive --verbose --recursive src tests)

## Run a single test
unit-test:
	$(call execute_in_env, PYTHONPATH=${PYTHONPATH}:src pytest -v tests/${test_run})

## Run all the unit tests
unit-tests:
	$(call execute_in_env, PYTHONPATH=$(PYTHONPATH):src pytest -v tests/)

## Run all checks
run-checks: run-flake unit-tests

## Make all
all: create-environment install-dependencies run-checks