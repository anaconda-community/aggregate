# Package-testing
Top ten priotity packages test suite to validate and quality check of its changes and its impact on the dependencies.


GitHub action CI template with:
* Bootstrapping Miniconda3 supporting Linux (x86, aarch64, ppc64le, s390x), macOS (x86, arm64)
* Randomized test environment names for parallel action executions
* Linting/testing with flake8/mypy/bandit/shellcheck/hadolint via pre-commit
* Testing via pytest including html and coverage report
* Abstraction layer via Makefile for local and remote execution of targets for easy reproducibility
* Mono Repo like behaviour via github action "on: path " feature
* Cron/manual triggered action cleanup action to wipe miniconda with all environments
