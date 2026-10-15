# Reference documentation

This page lists the specifications and the external documentation applicable to RS-Python.

## Copernicus

| Document | Usage |
|---|---|
| [Copernicus Sentinel missions](https://sentinels.copernicus.eu/) and [SentiWiki](https://sentiwiki.copernicus.eu/) | Description of the missions, products and ground segment. |
| [Copernicus operations - ground segment](https://sentiwiki.copernicus.eu/web/copernicus-operations) | Description of the acquisition (CADIP), auxiliary data (AUXIP) and production (PRIP) services, whose OData interfaces are used by the [external data sources](../rs-server/docs/doc/users/external-data-sources.md). |
| [Copernicus Data Space Ecosystem](https://dataspace.copernicus.eu/) and its [STAC API](https://documentation.dataspace.copernicus.eu/APIs/STAC.html) | Source of products and auxiliary data. |
| [Destination Earth](https://destination-earth.eu/) and [EarthDataHub](https://earthdatahub.destine.eu/) | Source of the Copernicus Digital Elevation Model. |

## EOPF and DPR processors

| Document | Usage |
|---|---|
| [EOPF project](https://eopf.copernicus.eu/) | The re-engineering of the Sentinel processors. |
| [EOPF CPM documentation](https://cpm.pages.eopf.copernicus.eu/eopf-cpm/main/index.html) and [source code](https://gitlab.eopf.copernicus.eu/cpm/eopf-cpm) | The Core Python Modules used by the processors. |
| [Task tables](https://cpm.pages.eopf.copernicus.eu/eopf-cpm/main/processor-orchestration-guide/tasktables.html) | Interface of the processors with the orchestration, see [Task tables and payload file](../rs-client-libraries/docs/doc/flows/tasktable-payload.md). |
| [Triggering usage and payload file](https://cpm.pages.eopf.copernicus.eu/eopf-cpm/main/processor-orchestration-guide/triggering-usage.html) | How the processors are triggered by [rs-dpr-service](../rs-dpr-service/docs/doc/index.md). |
| [Product types naming rules](https://cpm.pages.eopf.copernicus.eu/eopf-cpm/main/PSFD/3-product-types-naming-rules.html) | Names of the EOPF product types, e.g. `S03OLCEFR`. |
| [EOPF sample notebooks](https://github.com/EOPF-Sample-Service/eopf-sample-notebooks) | Examples to read and use the Zarr products. |

## Standards

| Standard | Usage |
|---|---|
| [SpatioTemporal Asset Catalog (STAC)](https://stacspec.org/) and its [specification](https://github.com/radiantearth/stac-spec) | Data model of all the products, see [Catalog data model and lifecycle](../rs-server/docs/doc/users/data-model.md). |
| [STAC API](https://github.com/radiantearth/stac-api-spec), with the [Filter](https://github.com/stac-api-extensions/filter), [Sort](https://github.com/stac-api-extensions/sort), [Transaction](https://github.com/stac-api-extensions/transaction), [Collection Transaction](https://github.com/stac-api-extensions/collection-transaction) and [Bulk Transaction](https://github.com/stac-utils/stac-fastapi) extensions | Interface of the [catalog](../rs-server/docs/doc/users/catalog.md) and of the [external data sources](../rs-server/docs/doc/users/external-data-sources.md). |
| [STAC extensions](https://stac-extensions.github.io/) | Metadata of the items, see [Catalog data model and lifecycle](../rs-server/docs/doc/users/data-model.md#extensions). The RS-Python specific ones are the [CADIP](https://github.com/RS-PYTHON/cadip-stac-extension), [ownership](https://github.com/RS-PYTHON/ownership-stac-extension) and [download](https://github.com/RS-PYTHON/download-stac-api-extension) extensions. |
| [OGC Common Query Language (CQL2)](https://docs.ogc.org/is/21-065r2/21-065r2.html) | Filters of the STAC API searches. |
| [OGC API - Processes](https://ogcapi.ogc.org/processes/) | Interface of the [staging](../rs-server/docs/doc/users/staging.md) and [processing](../rs-dpr-service/docs/doc/index.md) services. |
| [OData Version 4.01](https://www.odata.org/documentation/) | Interface of the Copernicus stations. |
| [OpenAPI](https://www.openapis.org/) | Description of the web services, displayed in the [Swagger page](../services/swagger.md). |
| [OAuth 2.0](https://oauth.net/2/) and [OpenID Connect](https://openid.net/developers/how-connect-works/) | Authentication of the users, with [Keycloak](https://www.keycloak.org/). |
| [OpenTelemetry](https://opentelemetry.io/docs/specs/) | Logs, metrics and traces. |
| [Zarr](https://zarr.dev/) | Format of the EOPF products. |

## Main open-source components

| Component | Documentation |
|---|---|
| [stac-fastapi](https://github.com/stac-utils/stac-fastapi), [stac-fastapi-pgstac](https://github.com/stac-utils/stac-fastapi-pgstac), [pgstac](https://github.com/stac-utils/pgstac) | Implementation of the catalog. |
| [pygeoapi](https://pygeoapi.io/) | Implementation of the OGC API - Processes services. |
| [FastAPI](https://fastapi.tiangolo.com/) | Web framework of the services. |
| [pystac](https://pystac.readthedocs.io/), [pystac-client](https://pystac-client.readthedocs.io/) | STAC Python libraries used by the rs-client-libraries. |
| [EODAG](https://eodag.readthedocs.io/) | Access to the external data sources. |
| [Prefect](https://docs.prefect.io/) | Workflow orchestration. |
| [Dask](https://docs.dask.org/), [Dask Gateway](https://gateway.dask.org/) | Parallel computing. |
| [JupyterHub](https://jupyterhub.readthedocs.io/) | Virtual environment. |
| [STAC Browser](https://github.com/radiantearth/stac-browser) | Web user interface of the STAC APIs. |
| [Kubernetes](https://kubernetes.io/docs/home/), [Helm](https://helm.sh/docs/), [Kustomize](https://kustomize.io/), [Ansible](https://docs.ansible.com/), [Terraform](https://developer.hashicorp.com/terraform/docs) | Deployment. |
| [Envoy Gateway](https://gateway.envoyproxy.io/), [Gateway API](https://gateway-api.sigs.k8s.io/), [cert-manager](https://cert-manager.io/docs/) | Exposition of the services. |
| [Keycloak](https://www.keycloak.org/documentation) | Identity and access management. |
| [CloudNativePG](https://cloudnative-pg.io/documentation/), [Velero](https://velero.io/docs/) | Databases and backups. |
| [Grafana](https://grafana.com/docs/), [Prometheus](https://prometheus.io/docs/), [Loki](https://grafana.com/docs/loki/latest/), [Tempo](https://grafana.com/docs/tempo/latest/), [Alloy](https://grafana.com/docs/alloy/latest/) | Monitoring. |

The complete list of the third-party components and of their licenses is given in the *Third-party components*
annexes.
