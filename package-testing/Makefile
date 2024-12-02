# Makefile for various tasks with or around the code.
#

SHELL := /bin/bash -o pipefail -o errexit

ARTIFACTS_PATH := artifacts
CONDA_ENV_NAME ?= package-testing

help:
	@fgrep -h "##" $(MAKEFILE_LIST) | fgrep -v fgrep | sed -e 's/\\$$//' | sed -e 's/##//'

environment:       ## Handles environment creation
	conda env create -f environment.yml --name $(CONDA_ENV_NAME) --force
	conda run --name $(CONDA_ENV_NAME) pip install -e .

pre-commit:        ## Run pre-commit against all files
	pre-commit run --all-files

test:              ## Run tests
	mkdir -p $(ARTIFACTS_PATH)
	python -m pytest \
		--junit-xml="$(ARTIFACTS_PATH)/test-report.xml" \
		--html="$(ARTIFACTS_PATH)/test-report.html" \
		--alluredir=allure-results \
		--cov \
		--cov-report html --cov-report html:$(ARTIFACTS_PATH)/cov_html \
		--cov-report xml --cov-report xml:$(ARTIFACTS_PATH)/cobertura.xml \
		--show-capture=all -vv .


.PHONY: all $(MAKECMDGOALS)
