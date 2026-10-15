# Welcome to RS-Python

The **Copernicus Reference System Python** (*RS-Python*, sometimes abbreviated **RSPY**) is an open-source
software solution to implement, maintain, deploy, operate and monitor
[Copernicus Sentinel](https://sentinels.copernicus.eu/) data processing workflows, based on the re-engineered
Level-0, Level-1 and Level-2 Sentinel data processors of the
[EOPF](https://eopf.copernicus.eu/) (Earth Observation Processing Framework) project.

It is developed for the [European Space Agency (ESA)](https://www.esa.int/) under the
[Copernicus programme](https://www.copernicus.eu/) of the European Union, and is distributed under the
[Apache License, Version 2.0](https://www.apache.org/licenses/LICENSE-2.0).

!!! tip "In a nutshell"

    RS-Python lets you **search** Sentinel data in the Copernicus ground segment (acquisition stations,
    auxiliary data, production services, archives), **stage** it into your own object storage and
    [STAC](https://stacspec.org/) catalog, **process** it with the official
    [DPR processors](rs-dpr-service/docs/doc/index.md) running on a [Dask](https://www.dask.org/) cluster,
    and **orchestrate** all of this with [Prefect](https://www.prefect.io/) flows - systematically or on demand.

## What is in the box?

From a functional point of view, RS-Python is made of:

| Component | What it does for you |
|---|---|
| [**rs-server**](rs-server/docs/doc/index.md) | Web services with fine access control: browse the external data sources (CADIP, AUXIP, PRIP stations) and the RS-Python catalog with a [STAC API](https://github.com/radiantearth/stac-api-spec), stage products into the catalog, get your object storage credentials. |
| [**DPR processors**](rs-dpr-service/docs/doc/index.md) | The Sentinel-1, Sentinel-2 and Sentinel-3 processors, delivered as Docker images and run on Dask clusters, triggered through an [OGC API - Processes](https://ogcapi.ogc.org/processes/) web service. |
| [**Prefect flows**](rs-client-libraries/docs/doc/flows/index.md) | Ready-to-use workflows to search, stage and process Sentinel products, from Level-0 to Level-2. |
| [**rs-client-libraries**](rs-client-libraries/docs/doc/index.md) | The Python library used by the flows to call the services. Use it to write your own flows. |
| [**Virtual environment**](services/virtual-environment/index.md) | A per-group workspace with [JupyterHub](https://jupyter.org/hub), [Prefect](https://www.prefect.io/) and [Dask](https://www.dask.org/) to develop, run and monitor your processing. |
| [**Infrastructure**](administration/deploy.md) | Everything needed to deploy the platform on a [Kubernetes](https://kubernetes.io/) cluster: identity and access management, databases, object storage, monitoring, security. |

See [Project organisation](getting-started/project-organisation.md) for a more detailed description of the
components and of the source code repositories.

## Who are you?

This documentation is organised by profile. Pick the one that matches your role:

<div class="grid cards" markdown>

-   :material-account: **User** (data operator, analyst)

    ---

    You run existing flows, then view and download the generated products.

    → [Quickstart](getting-started/quickstart.md), [Services](services/index.md),
    [Prefect flows](rs-client-libraries/docs/doc/flows/index.md)

-   :material-code-braces: **Flow developer** (processing chain developer, IVV)

    ---

    You customise the processing, write your own flows and integrate new processors.

    → [Advanced flow management](rs-client-libraries/docs/doc/advanced/customise-dpr-flow.md)

-   :material-shield-account: **Administrator** (and operator)

    ---

    You deploy and maintain the platform, manage the user accounts and rights, initialise the processing
    environment, monitor the platform and support the users. Operators use a subset of the administration tools,
    mainly the monitoring ones.

    → [Administration](administration/index.md)

-   :material-source-branch: **Software developer and contributor**

    ---

    You pull, run and modify the source code or the documentation of the project.

    → [Developers and contributors](developers/index.md)

</div>

## Essential features

RS-Python relies on state-of-the-art open-source tools and standards:

- **Standards for interoperability**: all the data, internal or external, is described with the
  [SpatioTemporal Asset Catalog (STAC)](https://stacspec.org/) specification and exposed with the
  [STAC API](https://github.com/radiantearth/stac-api-spec). Asynchronous services follow
  [OGC API - Processes](https://ogcapi.ogc.org/processes/).
- **Re-engineered processors**: the Copernicus processors are re-written in Python by the
  [EOPF](https://eopf.copernicus.eu/) project, on top of the
  [EOPF Core Python Modules (CPM)](https://cpm.pages.eopf.copernicus.eu/eopf-cpm/main/index.html), and produce
  [Zarr](https://zarr.dev/) products.
- **Parallel computing** with [Dask](https://www.dask.org/) clusters managed by
  [Dask Gateway](https://gateway.dask.org/).
- **Workflows as code** with [Prefect](https://www.prefect.io/): implement, schedule, chain and instrument your
  processing in Python.
- **Cloud native**: everything is containerised with [Docker](https://www.docker.com/) and deployed on a
  [Kubernetes](https://kubernetes.io/) cluster (hosted by [OVHcloud](https://www.ovhcloud.com/) for the
  reference platform) with [Ansible](https://www.ansible.com/) and [Helm](https://helm.sh/), data is stored in
  S3-compatible object storage and [PostgreSQL](https://www.postgresql.org/) databases.
- **Security**: identity and access management with [Keycloak](https://www.keycloak.org/), fine access rights
  per station and per catalog collection, API keys for long-running processing.
- **Observability**: logs, metrics and traces instrumented with [OpenTelemetry](https://opentelemetry.io/) and
  displayed in [Grafana](https://grafana.com/).
- **Virtual environment**: a [JupyterHub](https://jupyter.org/hub) workspace with the client libraries
  pre-installed.

Compared to the previous solutions, RS-Python gives more flexibility to the users to search, stage, process,
view and download specific products, and to customise their own processing flows.

## Copernicus ecosystem

RS-Python is part of the Copernicus ground segment ecosystem and interoperates with:

- the [Copernicus Sentinel missions](https://sentinels.copernicus.eu/) and their
  [SentiWiki](https://sentiwiki.copernicus.eu/) documentation,
- the [Copernicus Data Space Ecosystem (CDSE)](https://dataspace.copernicus.eu/), used as a data source,
- the [Destination Earth](https://destination-earth.eu/) data lake, whose
  [EarthDataHub](https://earthdatahub.destine.eu/) provides e.g. the Copernicus Digital Elevation Model,
- the [EOPF](https://eopf.copernicus.eu/) project, that delivers the processors and the
  [EOPF sample notebooks](https://github.com/EOPF-Sample-Service/eopf-sample-notebooks).

## Getting help

- Acronyms are explained in the [glossary](annexes/glossary.md).
- All the URLs of the platform services are listed in [Useful links](annexes/links.md).
- Report bugs and ask for features in the issue tracker of the relevant
  [GitHub repository](getting-started/project-organisation.md#source-code-organisation).
  For sensitive issues like security vulnerabilities, please contact <ops_coprs@airbus.com> directly instead of
  using the issue tracker.
