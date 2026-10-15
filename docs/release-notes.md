# Release notes

RS-Python is released as a whole: all the repositories of a release share the same version number, given by a git
tag, e.g. `v1.0a14`. The changes of each release are listed in the changelog of each repository, following the
[Keep a Changelog](https://keepachangelog.com/) format:

| Repository | Changelog | Releases |
|---|---|---|
| rs-server | [CHANGELOG](https://github.com/RS-PYTHON/rs-server/blob/develop/CHANGELOG.md) | [Releases](https://github.com/RS-PYTHON/rs-server/releases) |
| rs-helm | [CHANGELOG](https://github.com/RS-PYTHON/rs-helm/blob/develop/CHANGELOG.md) | [Releases](https://github.com/RS-PYTHON/rs-helm/releases) |
| rs-infra-core | [CHANGELOG](https://github.com/RS-PYTHON/rs-infra-core/blob/develop/CHANGELOG.md) | [Releases](https://github.com/RS-PYTHON/rs-infra-core/releases) |
| rs-infra-monitoring | [CHANGELOG](https://github.com/RS-PYTHON/rs-infra-monitoring/blob/develop/CHANGELOG.md) | [Releases](https://github.com/RS-PYTHON/rs-infra-monitoring/releases) |
| rs-server-deployment | [CHANGELOG](https://github.com/RS-PYTHON/rs-server-deployment/blob/develop/CHANGELOG.md) | [Releases](https://github.com/RS-PYTHON/rs-server-deployment/releases) |
| rs-workflow-env | [CHANGELOG](https://github.com/RS-PYTHON/rs-workflow-env/blob/develop/CHANGELOG.md) | [Releases](https://github.com/RS-PYTHON/rs-workflow-env/releases) |
| rs-workflow-deployment | [CHANGELOG](https://github.com/RS-PYTHON/rs-workflow-deployment/blob/develop/CHANGELOG.md) | [Releases](https://github.com/RS-PYTHON/rs-workflow-deployment/releases) |
| rs-client-libraries | | [Releases](https://github.com/RS-PYTHON/rs-client-libraries/releases), [PyPI](https://pypi.org/project/rs-client-libraries/) |
| rs-dpr-service | | [Releases](https://github.com/RS-PYTHON/rs-dpr-service/releases) |
| rs-demo | | [Releases](https://github.com/RS-PYTHON/rs-demo/releases) |
| rs-testmeans | | [Releases](https://github.com/RS-PYTHON/rs-testmeans/releases) |

The Docker images of each release are available in the
[GitHub Container Registry](https://github.com/orgs/RS-PYTHON/packages), with the release version as tag, and the
Helm charts in the [RS-Python Helm repository](https://home.rs-python.eu/rs-helm). See
[Repositories and CI/CD](developers/ci-cd.md) for the versioning rules.
