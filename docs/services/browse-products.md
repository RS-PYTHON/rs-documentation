# Browse products

The products of the external data sources (CADIP sessions, AUXIP auxiliary files, PRIP products) and of the
RS-Python catalog are all described as [STAC](https://stacspec.org/) items and can be searched with the same
[STAC API](https://github.com/radiantearth/stac-api-spec). You can browse them with:

- the [STAC browsers](#stac-browsers), from your web browser, without writing any code,
- the [Swagger page or any HTTP client](#with-the-stac-api),
- [Python code](#with-python), with the [rs-client-libraries](../rs-client-libraries/docs/doc/index.md).

Then you can [download the assets](#download-the-assets) of the catalog items.

## STAC concepts

| Concept | Description | Example |
|---|---|---|
| **Catalog** | The entry point of a STAC API (landing page), with links to its collections. | `/cadip`, `/auxip`, `/prip`, `/catalog` |
| **Collection** | A group of items. For the external data sources, collections are *virtual*: they are defined in the rs-server configuration to give a view of a station content, e.g. all the sessions of a station or all the products of a given type (see [External data sources](../rs-server/docs/doc/users/external-data-sources.md#collections)). In the catalog, collections are created by their owners. | `sgs` (all the sessions of the SGS station), `copernicus:s3-l0` |
| **Item** | A product, described by its metadata (`properties`), its footprint (`geometry`, `bbox`) and its files (`assets`). | A CADIP session, an auxiliary file, a Zarr product |
| **Asset** | A file of the item, with its location (`href`). In the catalog, the assets are stored in the S3 object storage. | A CADU chunk, a `.zarr` folder |

The metadata of each kind of product is described in
[STAC mapping of external data](../rs-server/docs/doc/users/stac-mapping.md) and
[Catalog data model and lifecycle](../rs-server/docs/doc/users/data-model.md).

## STAC browsers

The [STAC Browser](https://github.com/radiantearth/stac-browser) web applications offer a user interface to browse
the collections and items, display the footprints on a map, and search the items with filters. One instance is
deployed for each service:

| STAC browser | URL on the reference platform |
|---|---|
| Catalog | <https://stac-browser-catalog.ops.rs-python.eu/> |
| CADIP stations | <https://stac-browser-cadip.ops.rs-python.eu/> |
| AUXIP stations | <https://stac-browser-auxip.ops.rs-python.eu/> |
| PRIP stations | <https://stac-browser-prip.ops.rs-python.eu/> |

You are authenticated with your Keycloak account (OAuth2). Navigate between the collections and the items by
clicking on the links, and use the *Search* button to filter the items by date, footprint or with the
[queryables](#filter-the-items-with-cql2) of the collection.

## With the STAC API

All the services follow the [STAC API specification](https://github.com/radiantearth/stac-api-spec). Call them
from the [Swagger page](swagger.md), from your web browser (when you are logged in, you can click on the links of
the JSON responses to navigate), or from any HTTP client with your [API key](../getting-started/user-rights.md#api-keys).
`<service>` is one of `cadip`, `auxip`, `prip` or `catalog`:

| Endpoint | Description |
|---|---|
| `GET /<service>` | Landing page, with links to the collections. |
| `GET /<service>/collections` | List the collections you are allowed to read. |
| `GET /<service>/collections/{collection_id}` | Read one collection. |
| `GET /<service>/collections/{collection_id}/items` | Search the items of one collection. |
| `GET /<service>/collections/{collection_id}/items/{item_id}` | Read one item. |
| `GET` or `POST /<service>/search` | Search the items of all or some collections. |
| `GET /<service>/queryables`, `GET /<service>/collections/{collection_id}/queryables` | List the properties that can be used in the filters. |
| `GET /<service>/sortables`, `GET /<service>/collections/{collection_id}/sortables` | List the properties that can be used to sort the results (stations only). |

For example, to get the 10 most recent Sentinel-1A sessions of all the CADIP stations you can read:

```shell
curl -H "x-api-key: $RSPY_APIKEY" \
  "https://rspy.ops.rs-python.eu/cadip/search?filter=platform='sentinel-1a'&sortby=-published&limit=10"
```

### Search parameters

| Parameter | Description | Example |
|---|---|---|
| `collections` | Restrict the search to these collections (`/search` endpoint only). In the catalog, use `<owner>:<collection>` or `<collection>` for your own collections. | `collections=sgs,mti` |
| `ids` | Restrict the search to these item identifiers (`/search` endpoint only). | `ids=S1A_20231120061537234567` |
| `datetime` | Single date or interval, in [RFC 3339](https://www.rfc-editor.org/rfc/rfc3339) format. Open intervals use `..`. | `datetime=2026-01-01T00:00:00Z/2026-01-02T00:00:00Z` |
| `bbox` | Bounding box of the footprint (west, south, east, north). | `bbox=-10,35,30,60` |
| `filter` | [CQL2](https://docs.ogc.org/is/21-065r2/21-065r2.html) filter, see below. | `filter=platform='sentinel-1a'` |
| `filter-lang` | `cql2-text` (default) or `cql2-json`. With `POST /search`, the filter is usually given in `cql2-json`. | |
| `sortby` | Sort the results by one or several properties, `+` (default) for ascending and `-` for descending order. | `sortby=-datetime` |
| `limit` | Number of items per page. | `limit=100` |

The results are paginated: follow the `next` link of the response to get the next page (the stations also accept
a `page` parameter).

### Filter the items with CQL2

The [Filter extension](https://github.com/stac-api-extensions/filter) allows to search the items with a
[Common Query Language (CQL2)](https://docs.ogc.org/is/21-065r2/21-065r2.html) expression. The properties that you
can use are listed by the `queryables` endpoints. Some examples:

```text
# Comparison and logical operators
platform = 'sentinel-3a' AND product:type = 'S03OLCL0_'
cadip:downlink_status_ok = TRUE AND published > TIMESTAMP('2026-01-01T00:00:00Z')

# List of values
platform IN ('sentinel-1a', 'sentinel-1c')

# Text pattern
id LIKE 'S3A_2026%'
```

The same filter in CQL2 JSON, e.g. in the body of a `POST /catalog/search` request:

```json
{
  "collections": ["copernicus:s3-l0"],
  "filter-lang": "cql2-json",
  "filter": {
    "op": "and",
    "args": [
      {"op": "=", "args": [{"property": "platform"}, "sentinel-3a"]},
      {"op": "t_intersects", "args": [
        {"interval": [{"property": "start_datetime"}, {"property": "end_datetime"}]},
        {"interval": ["2026-08-07T00:00:00Z", "2026-08-08T00:00:00Z"]}
      ]}
    ]
  },
  "sortby": [{"field": "created", "direction": "desc"}],
  "limit": 10
}
```

The temporal operators such as `t_intersects` or `t_contains` are used to select the auxiliary files needed by
the processors, see [Task tables and payload file](../rs-client-libraries/docs/doc/flows/tasktable-payload.md#auxiliary-data-selection-policies).

!!! note "External data sources"

    For the stations, rs-server translates the STAC request into an [OData](https://www.odata.org/) request
    sent to the station. Only the operators supported by the stations can be used, see
    [STAC mapping of external data](../rs-server/docs/doc/users/stac-mapping.md#odata-support-of-the-stations).

## With Python

The [rs-client-libraries](../rs-client-libraries/docs/doc/index.md) wrap the
[pystac-client](https://pystac-client.readthedocs.io/) library. They are already installed in
[JupyterHub](virtual-environment/jupyterhub.md):

```python
import os
from rs_client.rs_client import RsClient

# Read the URL and your API key from the environment variables
rs_client = RsClient(os.environ["RSPY_WEBSITE"], os.environ["RSPY_APIKEY"])

# Search the CADIP stations
cadip_client = rs_client.get_cadip_client()
sessions = cadip_client.search(
    collections=["sgs"],
    stac_filter={"op": "=", "args": [{"property": "platform"}, "sentinel-3a"]},
    sortby="-published",
    limit=10,
)
for session in sessions:
    print(session.id, session.properties["published"])

# Search your catalog collections
catalog_client = rs_client.get_catalog_client()
items = catalog_client.search(
    collections=["s3-l0"],  # i.e. "<your-login>:s3-l0"
    timestamp="2026-08-07T00:00:00Z/2026-08-08T00:00:00Z",
    limit=100,
)
```

See [rs-client-libraries](../rs-client-libraries/docs/doc/index.md) and
[Create a custom flow](../rs-client-libraries/docs/doc/advanced/custom-flow.md) for more examples.

## Download the assets

The assets of the catalog items are stored in the S3 object storage. Their `href` field gives their S3 location,
e.g. `s3://rspython-ops-catalog-copernicus-s3-l0/S03OLCL0__20260807T020505_0119_A274_T366.zarr`. You need the
`download` right on the collection (see [User rights](../getting-started/user-rights.md#catalog)).

### Through the catalog

Each asset has an `alternate` HTTPS link to the `download` endpoint of the catalog:

```text
GET /catalog/collections/{owner}:{collection}/items/{item_id}/download/{asset_name}
```

It checks your rights, then redirects you to a temporary [presigned URL](https://docs.aws.amazon.com/AmazonS3/latest/userguide/using-presigned-url.html)
of the S3 object. Use it for files; for folder assets such as Zarr products, use the S3 access below.

### With your S3 credentials

[OSAM](../rs-server/docs/doc/users/osam.md) gives you read access to the buckets of the collections you can
download. Get your personal credentials from the `/storage/account/credentials` endpoint, e.g.
<https://rspy.ops.rs-python.eu/storage/account/credentials> (or with the [Swagger page](swagger.md)):

```json
{
  "access_key": "...",
  "secret_key": "...",
  "endpoint": "https://s3.<region>.io.cloud.ovh.net",
  "region": "<region>"
}
```

Then use any S3 client, e.g. [s3cmd](https://s3tools.org/s3cmd) or the [AWS CLI](https://aws.amazon.com/cli/):

```shell
export AWS_ACCESS_KEY_ID=<access_key> AWS_SECRET_ACCESS_KEY=<secret_key>
aws s3 ls --endpoint-url <endpoint> s3://<bucket>/
aws s3 cp --recursive --endpoint-url <endpoint> s3://<bucket>/<product>.zarr ./<product>.zarr
```

Or from Python, after [saving your credentials](../getting-started/setup-environment.md) in the `S3_*`
environment variables:

```python
from rs_common.prefect_utils import s3_download_file

await s3_download_file("s3://<bucket>/<path/to/file>", "./local_file")
```

Zarr products can also be opened directly from the object storage, without downloading them, e.g. with
[xarray](https://docs.xarray.dev/) or the [EOPF](https://cpm.pages.eopf.copernicus.eu/eopf-cpm/main/index.html)
libraries, see the [EOPF sample notebooks](https://github.com/EOPF-Sample-Service/eopf-sample-notebooks).
