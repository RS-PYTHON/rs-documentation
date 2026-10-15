# Developers and contributors

This section gathers the information, tutorials and tips for the developers of the team and the occasional
contributors, to:

- pull the source code and open it in an IDE, see [Coding environment](coding-environment.md),
- run the whole system on your computer, see [Local mode](../rs-demo/docs/local-mode.md),
- understand the architecture, see [System architecture](architecture.md),
- modify the code, test the changes, push them and open a pull request, see [Contributing](contributing.md),
- understand the CI/CD and the dependencies between the repositories, see [Repositories and CI/CD](ci-cd.md),
- deploy and test your changes on a cluster, see [Deploy RS-Python](../administration/deploy.md),
- find the interface specifications, see [Reference documentation](reference-documentation.md) and
  [Python API documentation](python-api.md),
- update this documentation, see [Generate the documentation](generate-documentation.md).

The documentation specific to each repository is in the repository itself, starting from its `README.md` file, e.g.
the [rs-server developer manual](../rs-server/docs/doc/dev/developer_manual.md) or the
[Dask images](../rs-workflow-env/docs/dask_images.md).

## Local mode and cluster mode

RS-Python runs in two modes:

| | Local mode | Cluster mode |
|---|---|---|
| Purpose | Development and tests, on your computer. | Integration, validation and operations. |
| Deployment | [Docker Compose](https://docs.docker.com/compose/) file of [rs-demo](../rs-demo/docs/local-mode.md). | Kubernetes cluster, see [Deploy RS-Python](../administration/deploy.md). |
| Authentication | None: all the users have all the rights. | Keycloak, API keys. |
| External data sources | Mockups from [rs-testmeans](../rs-testmeans/README.md). | Real stations (and mockups on test platforms). |
| Object storage | [SeaweedFS](https://github.com/seaweedfs/seaweedfs) container. | Cloud provider object storage. |
| Dask | One container per Dask cluster, each one running its own Dask Gateway server. | One Dask Gateway, Dask clusters created on demand. |
| Prefect | A Prefect server and one worker container per work pool. | A Prefect server per user group, with workers and work pools. |
| Jupyter | A Jupyter server container. | JupyterHub, one session per user. |
| Gateway | An [nginx](https://nginx.org/) container that exposes the services on <http://localhost>. | Envoy Gateway, with a domain name and TLS certificates. |

![Local mode and cluster mode](../images/local-and-cluster-modes.svg)
