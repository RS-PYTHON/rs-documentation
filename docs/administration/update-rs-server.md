# Update rs-server parameters

The RS-Python services are deployed by [rs-server-deployment](../rs-server-deployment/README.md), with the Helm
charts of [rs-helm](../rs-helm/README.md). Their parameters are set in the `values.yaml` file of each application of
rs-server-deployment, which takes most of its values from your inventory. After a modification, redeploy the
application as described in [Update infrastructure parameters](update-infrastructure.md), with
`package_paths` set to `~/rs-server-deployment/apps/`. The available parameters of each chart are described in its
README, see [rs-helm](../rs-helm/README.md).

The main parameters are described below.

## External data sources

| What | Where |
|---|---|
| URL and credentials of each station (CADIP, AUXIP, PRIP, LTA, CDSE...) | `rs-server-station-secrets` application ([chart](https://github.com/RS-PYTHON/rs-helm/blob/develop/charts/rs-server-station-secrets/README.md)), filled from the `rs_server_station_secrets` inventory variables. These secrets are used by the search services and by the staging. |
| List of the stations of each service | `rs-server-adgs`, `rs-server-cadip` and `rs-server-prip` applications (`app.station` values). |
| Virtual STAC collections of the stations | The `*_search_config.yaml` files of the [rs-server-adgs](https://github.com/RS-PYTHON/rs-helm/tree/develop/charts/rs-server-adgs/config), [rs-server-cadip](https://github.com/RS-PYTHON/rs-helm/tree/develop/charts/rs-server-cadip/config) and [rs-server-prip](https://github.com/RS-PYTHON/rs-helm/tree/develop/charts/rs-server-prip/config) charts, see [External data sources](../rs-server/docs/doc/users/external-data-sources.md#collections). |

## Object storage buckets and data lifecycle

The `rs-catalog-staging-configmap` application ([chart](https://github.com/RS-PYTHON/rs-helm/blob/develop/charts/rs-catalog-staging-configmap/README.md))
defines, in a CSV table, in which bucket each product is stored and for how long. It is used by:

- the staging and the processing flows, to choose the bucket where the assets are written,
- the catalog, to set the expiration date of the items,
- OSAM, to compute the object storage rights of the users.

Each line has 5 columns: `owner, collection, product type, expiration delay in days, bucket name`. For example:

```csv
*, *, *, 30, rspython-ops-catalog-all-production
copernicus, s1-aux, *, 40, rspython-ops-catalog-copernicus-s1-aux
copernicus, s1-aux, AUX_OBMEMC, 7300, rspython-ops-catalog-copernicus-s1-aux-infinite
```

To find the settings of an item, the first matching line is searched in this order:

1. the line with the same `owner`, `collection` and `product type`,
2. else the line with the same `owner` and `collection`, and `*` as product type,
3. else the line with the same `owner` and `product type`, and `*` as collection,
4. else the line with the same `owner`, and `*` as collection and product type,
5. else the default line `*, *, *`.

This allows to:

- control the costs: each bucket contains items with the same retention duration, so the expired items can be
  deleted easily (see [Catalog data model and lifecycle](../rs-server/docs/doc/users/data-model.md#data-lifecycle)),
- keep some items forever, e.g. auxiliary files or digital elevation models,
- isolate the production of a given owner, with a specific retention duration.

!!! note

    Bucket names cannot contain `_` characters with some object storage providers: replace them by another
    character, e.g. `x`. The buckets must exist before they are used.

The table is read by OSAM, that serves it to the other services. OSAM reloads it automatically when the config
map is updated (Kubernetes may take a minute to update the mounted file). Then run the OSAM synchronisation so
that the users get the rights on the new buckets, see
[Create accounts and assign permissions](accounts-permissions.md#synchronise-the-object-storage-rights).

## Staging

| What | Where |
|---|---|
| Number and size of the workers of the staging Dask cluster | `rs_server_staging.dask` inventory variables, used by the `dask-cluster-staging` application that keeps the staging cluster running. |
| Staging service settings (timeouts, retries...) | `rs-server-staging` application values. |

## DPR processors

rs-dpr-service is deployed once per Python and Dask version used by the processors
(`rs-dpr-service-py-<python>-dask-<dask>` applications), because a Dask client must use the same versions as the
Dask cluster it connects to. Each instance serves the `/dpr/processes/<processor>` routes of its processors. See
[DPR processors](../rs-dpr-service/docs/doc/index.md#deployment).

## Other parameters

| What | Where |
|---|---|
| Expiration of the catalog items, presigned URL lifespan, data lifecycle period | `rs-server-catalog` application values. |
| OSAM synchronisation period and credentials cache | `rs-server-osam` application values. |
| STAC browsers | `stac-browser-*` applications. |
| Mockups of the stations (for test platforms) | `mockup-*` applications. |
