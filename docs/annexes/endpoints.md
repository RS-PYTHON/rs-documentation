# Endpoints and permissions

This page summarises the HTTP endpoints of the RS-Python web services and the [Keycloak roles](../getting-started/user-rights.md#available-rights)
they require. Their detailed documentation (parameters, request and response bodies) is in the
[Swagger page](../services/swagger.md). In local mode, no authentication nor role is required.

All the endpoints require to be authenticated, with an OAuth2 session cookie or an API key, except the
documentation.

## Documentation and authentication

| Method | Endpoint | Description | Role |
|---|---|---|---|
| `GET` | `/docs`, `/openapi.json` | Aggregated Swagger page and OpenAPI specification of all the services. | None |
| `GET` | `/auth/login`, `/auth/logout` | OAuth2 login and logout. | None |
| `GET` | `/auth/me` | Show your user name and roles. | None |

## External data sources

`<service>` is `cadip`, `auxip` or `prip`. `<station>` is the station of the requested collection, see
[External data sources](../rs-server/docs/doc/users/external-data-sources.md).

| Method | Endpoint | Description | Role |
|---|---|---|---|
| `GET` | `/<service>` | Landing page (STAC catalog). | `rs_<service>_landing_page` |
| `GET` | `/<service>/conformance` | Conformance classes. | `rs_<service>_landing_page` |
| `GET` | `/<service>/collections` | Collections you are allowed to read. | `rs_<service>_landing_page` |
| `GET` | `/<service>/collections/{collection_id}` | One collection. | `rs_<service>_<station>_read` |
| `GET` | `/<service>/collections/{collection_id}/items` | Items of a collection. | `rs_<service>_<station>_read` |
| `GET` | `/<service>/collections/{collection_id}/items/{item_id}` | One item (a session for CADIP). | `rs_<service>_<station>_read` |
| `GET`, `POST` | `/<service>/search` | Search the items of one or several collections. | `rs_<service>_<station>_read` for each station |
| `GET` | `/<service>/queryables`, `/<service>/collections/{collection_id}/queryables` | Properties that can be used in the filters. | idem |
| `GET` | `/<service>/sortables`, `/<service>/collections/{collection_id}/sortables`, `/<service>/collections-sortables` | Properties that can be used to sort the results. | idem |

## Catalog

`{collection_id}` is `<owner>:<collection>`, or `<collection>` for your own collections. You always have all the
rights on your own collections.

| Method | Endpoint | Description | Role |
|---|---|---|---|
| `GET` | `/catalog/`, `/catalog/conformance` | Landing page and conformance classes. | None |
| `GET` | `/catalog/collections` | Collections you are allowed to read. | None (the result is filtered) |
| `GET` | `/catalog/collections/{collection_id}` | One collection. | `rs_catalog_<owner>:<collection>_read` |
| `GET` | `/catalog/collections/{collection_id}/items`, `/catalog/collections/{collection_id}/items/{item_id}` | Items of a collection, one item. | `rs_catalog_<owner>:<collection>_read` |
| `GET`, `POST` | `/catalog/search` | Search the items. | `rs_catalog_<owner>:<collection>_read` for each collection |
| `GET` | `/catalog/queryables`, `/catalog/collections/{collection_id}/queryables` | Properties that can be used in the filters. | idem |
| `GET` | `/catalog/collections/{collection_id}/items/{item_id}/download/{asset}` | Redirect to a temporary download URL of an asset. | `rs_catalog_<owner>:<collection>_download` |
| `POST` | `/catalog/collections` | Create a collection. | `rs_catalog_<owner>:<collection>_write` |
| `PUT`, `PATCH`, `DELETE` | `/catalog/collections/{collection_id}` | Update or delete a collection and its items. | `rs_catalog_<owner>:<collection>_write` |
| `POST` | `/catalog/collections/{collection_id}/items` | Add an item. | `rs_catalog_<owner>:<collection>_write` |
| `POST` | `/catalog/collections/{collection_id}/bulk_items` | Add several items at once. | `rs_catalog_<owner>:<collection>_write` |
| `PUT`, `PATCH`, `DELETE` | `/catalog/collections/{collection_id}/items/{item_id}` | Update or delete an item. | `rs_catalog_<owner>:<collection>_write` |
| `GET` | `/catalog/_mgmt/ping`, `/catalog/_mgmt/health` | Liveness and readiness. | None |

## Staging

The staging service follows [OGC API - Processes](https://ogcapi.ogc.org/processes/), with a single `staging`
process.

| Method | Endpoint | Description | Role |
|---|---|---|---|
| `GET` | `/processes`, `/processes/{resource}` | List and describe the processes. | `rs_processes_staging_read` |
| `POST` | `/processes/staging/execution` | Start a staging job. | `rs_processes_staging_execute`, and `rs_processes_staging_download_<station>` for each station to download from |
| `GET` | `/jobs`, `/jobs/{job_id}`, `/jobs/{job_id}/results` | List the jobs, get the status and results of a job. | `rs_processes_staging_read` |
| `DELETE` | `/jobs/{job_id}` | Dismiss a job. | `rs_processes_staging_dismiss` |

## Processing (DPR)

The processing service follows [OGC API - Processes](https://ogcapi.ogc.org/processes/), with one process per DPR
processor, plus the `conv_safe_zarr` conversion process.

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/dpr/processes` | List the processors. |
| `GET` | `/dpr/processes/{processor}` | Get the task table of a processor. |
| `POST` | `/dpr/processes/{processor}/execution` | Run a processor on a Dask cluster, with a payload file. |
| `GET` | `/dpr/jobs`, `/dpr/jobs/{job_id}` | List the jobs, get the status of a job. |
| `GET` | `/dpr/jobs/{job_id}/logs` | Stream the logs of a job. |
| `DELETE` | `/dpr/jobs/{job_id}` | Cancel a job. |

## OSAM

| Method | Endpoint | Description | Role |
|---|---|---|---|
| `GET` | `/storage/account/credentials` | Get your personal S3 credentials. | None |
| `POST` | `/storage/accounts/update` | Create and delete the object storage accounts according to the Keycloak accounts. | `rs_osam_update` |
| `POST` | `/storage/account/{user}/update` | Compute and apply the object storage rights of a user. | `rs_osam_update` |
