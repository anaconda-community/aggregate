# aggregate

This project manages the feedstocks and starts the build pipeline for community repo.
All the code in this repository is executed via GitHub Actions.

## Actions

### Manual actions
#### Add repo
To add a new repo go to the 'Actions' tab in GitHub and select 'Add repo' action.
For input use a conda-forge feedstock. Separate multiple feedstocks by comma.

Example: `7za-feedstock,7zip-feedstock`

For all the feedstocks in the list, the [tool](#tools) `crawl_deptree.py` will be used to find dependencies.
The resulting list of feedstocks and their dependencies will be forked from conda-forge and added to `manifest.yaml`.
If the feedstock has already been forked it will not attempt to fork again. If the feedstock is already in `manifest.yaml` then the file won't be modified.
A **Pull Request** will be opened that will contain any changes made to `manifest.yaml`.

#### Remove repo
To remove a repo go to the 'Actions' tab in GitHub and select 'Remove repo' action.
For input use the repo name. 

Example: `7za-feedstock`

All feedstocks in the list will be removed from `manifest.yaml` and the forks will be deleted.
A **Pull Request** will be opened that will contain the changes to `manifest.yaml`.

### Automatic actions

#### Build
If a **Pull Request** is opened or merged where manifest.yaml has been updated the file will be parsed and additions or changes to it will
trigger a new build.
The action will use the [tool](#tools) `crawl_deptree.py` to find dependencies of the feedstocks to be built and create a build order.
If the PR is being merged then the build will run against "main" branch, otherwise it will be on the **Pull Request** branch.

*There is also a "Manual build feedstock" workflow that takes a list of feedstocks to build as input to run builds manually.

#### Update repo
On a schedule defined in update-repo.yml all forks will be synced with upstream.
For any feedstocks that are updated we will use the [tool](#tools) `crawl_deptree.py` to find any new dependencies. Any new dependencies will be forked and added to manifest
as well as any commit hashes that were updated. A **Pull Request** will be created with any changes to `manifest.yaml`.

In places were we are just checking if existing feedstocks were updated we use **yq** to modify `manifest.yaml` instead of **abs-cli** for performance reasons.
There are concerns about how this action will scale once we have significantly more feedstocks.

#### Sync Pinnings
Pinnings are updated via the "Sync pinnings" workflow that runs on a schedule. This will merge the pinnings from community repo, anacondarecipes, and conda-forge.
If an entry exists in `conda_build_config_community.yaml` it will be given preference. Next is AnacondaRecipes, and last is conda-forge. A **Pull Request** will be created with the changes.

#### Integration test
Integration test is run via the "Integration Test" workflow that runs on a schedule.
This action will increment the build number in community-integration-test-feedstock and then run a build against that change.
It will then wait up to 10 minutes for the new build to appear in community_test channel and attempt to install it.
Results are reported to DataDog

#### SBOM Artifact check
SBOM artifact check is run via the "SBOM artifact check" workflow that runs on a schedule.
This action will download the repodata and sboms/index files from anaconda.cloud and report any packages in repodata without a matching file in sboms to DataDog

## Non-standard or notable feedstocks

Unless noted below, all feedstocks should be a strict fork from [conda-forge](https://github.com/conda-forge) without modification.

### Redis-feedstock
[redis-feedstock](https://github.com/anaconda-community/redis-feedstock)

This feedstock in conda-forge is a public archive which means we were not able to fork it. We made a manual copy but it will not be updated by any automation.

### Community-meta-feedstock
[community-meta-feedstock](https://github.com/anaconda-community/community-meta-feedstock)

This is a "virtual" package. We use it for libblas, libcblas, liblapack, liblapacke to force those packages to openblas-devel

### community-integration-test-feedstock
[community-integration-test-feedstock](https://github.com/anaconda-community/community-integration-test-feedstock)

This is colorama feedstock re-named to be used for [integration tests](#integration-test).

### scipy-feedstock
[scipy-feedstock](https://github.com/anaconda-community/scipy-feedstock)

This feedstock has been modified from its parent with the addition of `recipe_append.yaml` to get the build to work. 
Because this is an additional file and not a modification of an existing file we don't expect any issues syncing with the upstream repo.

## Pinnings
We maintain a list of pinned packages in `conda_build_config.yaml` that we sync from AnacondaRecipes and conda-forge/conda-forge-pinning-feedstock.
Feedstocks for packages in AnacondaRecipes conda_build_config should not be included in community repo.
To support additional pinnings for community repo we have a file `conda_build_config_community.yaml` that will be merged with `conda_build_config.yaml` when the [sync-pinnings](#sync-pinnings) workflow is run


In order to remove a pinning from either AnacondaRecipes or conda-forge pinnings add the key with an empty map to `conda_build_config_community.yaml` and the github action will remove it from the final file.

Example: `key: {}`

## Tools
Tools to be used in github workflows. See [tools/README.md](tools/README.md)

## Development
### Building feedstocks locally
To build a feedstock locally you will need to install `abs-cli` and `docker`

1. Setup your workspace. You can change the ref from 'main' to your branch to test changes that aren't merged.
```text
abs workspace init -a https://github.com/anaconda-community/aggregate -r main
abs workspace add-recipe <feedstock>
```
2. Run build.
```
docker \
  run --rm --init \
  -v "<path to workspace>:/workspace" \
  -v "<path to workspace>/feedstocks/<feedstock>:/recipe" \
  -w "/workspace/aggregate" \
  public.ecr.aws/y0o4y9o3/anaconda-pkg-build:latest \
  /bin/bash \
  -c \
  'conda build "/recipe" --no-test --output-folder "/workspace/output" --croot "/workspace/croot" --cache-dir "/workspace/cache-dir" --channel "https://staging.continuum.io/community/dev" --channel "https://staging.continuum.io/community/seed"'
```
Note: This command may change. To get the latest command see https://github.com/anaconda-distribution/rocket-platform/blob/main/sdk/src/abs/workspace.py or check the logs in a recent Prefect build.

### Run integration test locally
To run the integration test locally,
- install [Act](https://github.com/nektos/act)
- configure act to use a runner
- create a github personal access token and put in a `.env` file

Run update-manifest job:
```
act -j update-manifest -W .github/workflows/integration-test.yml -s GITHUB_TOKEN
```