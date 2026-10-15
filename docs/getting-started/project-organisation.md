# Project organisation

This page describes the RS-Python components from a functional point of view (what you can do with them), then
explains where they are implemented in the [RS-PYTHON GitHub organisation](https://github.com/RS-PYTHON).

![RS-Python functional overview](../images/functional-overview.svg)

## Components for the users

### Reference System web services

The web services are implemented by [rs-server](../rs-server/docs/doc/index.md) and
[rs-dpr-service](../rs-dpr-service/docs/doc/index.md). They are all protected by authentication and fine-grained
authorisation (see [User rights and API keys](user-rights.md)) and documented in a single
[Swagger page](../services/swagger.md).

- **External data sources**: [STAC API](https://github.com/radiantearth/stac-api-spec) services to search the
  Copernicus ground segment in read-only mode:
  [CADIP](../rs-server/docs/doc/users/external-data-sources.md#cadip-stations) acquisition stations (raw data
  sessions), [AUXIP](../rs-server/docs/doc/users/external-data-sources.md#auxip-adgs-stations) stations (auxiliary
  data) and [PRIP](../rs-server/docs/doc/users/external-data-sources.md#prip-stations) production services
  (Level-0, Level-1 and Level-2 products).
- **Catalog**: a [STAC API](https://github.com/radiantearth/stac-api-spec) service to search, read and update
  the RS-Python [catalog](../rs-server/docs/doc/users/catalog.md), stored in a [PostgreSQL](https://www.postgresql.org/)
  database. Each user owns their collections.
- **Staging**: an [OGC API - Processes](https://ogcapi.ogc.org/processes/) service that
  [copies products](../rs-server/docs/doc/users/staging.md) from the external data sources into the RS-Python
  object storage and catalog.
- **Processing**: an [OGC API - Processes](https://ogcapi.ogc.org/processes/) service that runs the
  [DPR processors](../rs-dpr-service/docs/doc/index.md) on a Dask cluster.
- **OSAM** (Object Storage Access Manager): [get your S3 credentials](../rs-server/docs/doc/users/osam.md) to
  download the products from the object storage.

### STAC browsers

The [STAC Browser](https://github.com/radiantearth/stac-browser) web interfaces allow to
[browse the products](../services/browse-products.md) of the stations and of the catalog without writing any code.

### DPR processors

The [DPR processors](../rs-dpr-service/docs/doc/index.md) generate the Sentinel products. They are delivered by
the [EOPF](https://eopf.copernicus.eu/) project as Python packages, embedded into Docker images by RS-Python, and
run on the Reference System [Dask](https://www.dask.org/) clusters.

### Prefect

[Prefect](https://www.prefect.io/) runs and monitors the [processing flows](../rs-client-libraries/docs/doc/flows/index.md):

- **on-demand flows**, started by a user from the Prefect dashboard or from Python code,
- **systematic flows**, started automatically when new data is available (see
  [Systematic processing](../rs-client-libraries/docs/doc/advanced/systematic-processing.md)),
- **custom flows**, written by the users themselves (see
  [Create a custom flow](../rs-client-libraries/docs/doc/advanced/custom-flow.md)).

The flows call the Reference System services with the [rs-client-libraries](../rs-client-libraries/docs/doc/index.md).

### JupyterHub

[JupyterHub](https://jupyter.org/hub) provides a [virtual environment](../services/virtual-environment/jupyterhub.md)
in which the RS-Python libraries are already installed. Use its notebooks to call the services, test your code and
customise your Prefect flows.

### Dask

[Dask](https://www.dask.org/) runs the DPR processors and the staging tasks in parallel. The
[Dask dashboard](../services/virtual-environment/dask.md) shows the progress of a processor run at a lower level
than Prefect.

### API Key Manager

The [API Key Manager](user-rights.md#api-keys) creates the API keys that hold your authentication and
authorisation information, used to call the services and run the Prefect flows.

## Components for the administrators

In addition to the components above, the administrators use:

- the [Keycloak](https://www.keycloak.org/) administration console, to
  [manage the user accounts and their rights](../administration/accounts-permissions.md),
- the object storage provider console,
- the [OSAM](../rs-server/docs/doc/users/osam.md) service, to synchronise the user accounts and rights between
  Keycloak and the S3 object storage,
- [Grafana](https://grafana.com/) and the [OpenTelemetry](https://opentelemetry.io/) instrumentation, to
  [monitor](../administration/monitoring.md) the logs, metrics, traces and resources of the platform.

## Source code organisation

The source code is hosted in the [RS-PYTHON GitHub organisation](https://github.com/RS-PYTHON). Each repository
has a `README.md` file that describes its content.

### Documentation repositories

| Repository | Description |
|---|---|
| [rs-documentation](https://github.com/RS-PYTHON/rs-documentation) | System-level documentation; aggregates the documentation of all the other repositories into this [website](https://home.rs-python.eu/rs-documentation/). |
| [rs-demo](https://github.com/RS-PYTHON/rs-demo) | [Jupyter](https://jupyter.org/) notebooks showcasing the features of the system, and the [local mode](../rs-demo/docs/local-mode.md) to run the whole system on your computer. |
| [RS-PYTHON.github.io](https://github.com/RS-PYTHON/RS-PYTHON.github.io) | Sources of the project [landing page](https://home.rs-python.eu/). |

### Python repositories

| Repository | Description |
|---|---|
| [rs-server](https://github.com/RS-PYTHON/rs-server) | The rs-server web services: [STAC](https://stacspec.org/) access to the external data sources and to the catalog, staging, OSAM, frontend. |
| [rs-dpr-service](https://github.com/RS-PYTHON/rs-dpr-service) | The web service that retrieves the [task tables](https://cpm.pages.eopf.copernicus.eu/eopf-cpm/main/processor-orchestration-guide/tasktables.html) and [triggers the DPR processors](https://cpm.pages.eopf.copernicus.eu/eopf-cpm/main/processor-orchestration-guide/triggering-usage.html) in a Dask cluster. |
| [rs-client-libraries](https://github.com/RS-PYTHON/rs-client-libraries) | The `rs_client` library (which simplifies calling the services), the `rs_workflows` Prefect flows and the `rs_common` utilities. |
| [rs-testmeans](https://github.com/RS-PYTHON/rs-testmeans) | Mockups of the external data sources (CADIP, AUXIP, PRIP, LTA) and of a DPR processor, used for the tests and the demos. |
| [opentelemetry-instrumentation-eopf](https://github.com/RS-PYTHON/opentelemetry-instrumentation-eopf) | [OpenTelemetry](https://opentelemetry.io/) instrumentation for EOPF. |

### STAC extensions

| Repository | Description |
|---|---|
| [cadip-stac-extension](https://github.com/RS-PYTHON/cadip-stac-extension) | Describes Copernicus CADIP sessions from the acquisition ground stations as STAC items. |
| [ownership-stac-extension](https://github.com/RS-PYTHON/ownership-stac-extension) | Expresses the ownership of STAC collections and items. |
| [download-stac-api-extension](https://github.com/RS-PYTHON/download-stac-api-extension) | STAC API extension that adds a dedicated endpoint to download an asset. |

### Infrastructure repositories

| Repository | Description |
|---|---|
| [rs-infra-core](https://github.com/RS-PYTHON/rs-infra-core) | [Terraform](https://www.terraform.io/) and [Ansible](https://www.ansible.com/) playbooks to create the Kubernetes cluster and deploy the core infrastructure components. |
| [rs-infra-monitoring](https://github.com/RS-PYTHON/rs-infra-monitoring) | The monitoring components (Grafana, Prometheus, Loki, Tempo, Alloy) deployed on top of the core infrastructure. |
| [rs-workflow-env](https://github.com/RS-PYTHON/rs-workflow-env) | The virtual environment components (JupyterHub, Prefect, Dask Gateway, API Key Manager) and the Docker images of the Dask clusters and of JupyterHub. |
| [rs-server-deployment](https://github.com/RS-PYTHON/rs-server-deployment) | The deployment of the rs-server services, rs-dpr-service, STAC browsers, databases and mockups on top of the core infrastructure. |
| [rs-helm](https://github.com/RS-PYTHON/rs-helm) | The [Helm charts](https://helm.sh/) of the rs-server services, rs-dpr-service, STAC browsers and mockups. |
| [rs-workflow-deployment](https://github.com/RS-PYTHON/rs-workflow-deployment) | The deployment of the Prefect flows and automations delivered by default. |

The security components (e.g. [Wazuh](https://wazuh.com/) and [NeuVector](https://github.com/neuvector/neuvector))
are deployed from a separate, non-public repository.

### Tool repositories

| Repository | Description |
|---|---|
| [actions](https://github.com/RS-PYTHON/actions) | Reusable [GitHub Actions](https://docs.github.com/en/actions) workflows and composite actions for all the RS-PYTHON repositories. |

The dependencies between the repositories and their CI/CD are described in
[Repositories and CI/CD](../developers/ci-cd.md).
