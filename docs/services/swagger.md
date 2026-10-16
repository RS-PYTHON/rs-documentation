# Swagger

The [Swagger UI](https://swagger.io/tools/swagger-ui/) page of the rs-server
[frontend](../rs-server/docs/doc/users/frontend.md) documents all the RS-Python web service endpoints and lets you
call them directly from your browser, without writing Python code or running Prefect flows:

- on the reference platform: <https://rspy.ops.rs-python.eu/docs>
- the corresponding [OpenAPI](https://www.openapis.org/) specification: <https://rspy.ops.rs-python.eu/openapi.json>

Replace `ops.rs-python.eu` by the domain name of your own platform. The endpoints are grouped by service:

| Section | Endpoints | Description |
|---|---|---|
| [ADGS stations](https://rspy.ops.rs-python.eu/docs#/ADGS%20stations) | `/auxip/...` | Search the auxiliary data of the AUXIP stations ([documentation](../rs-server/docs/doc/users/external-data-sources.md#auxip-adgs-stations)). |
| [CADIP stations](https://rspy.ops.rs-python.eu/docs#/CADIP%20stations) | `/cadip/...` | Search the sessions of the CADIP stations ([documentation](../rs-server/docs/doc/users/external-data-sources.md#cadip-stations)). |
| [PRIP stations](https://rspy.ops.rs-python.eu/docs#/PRIP%20stations) | `/prip/...` | Search the products of the PRIP stations ([documentation](../rs-server/docs/doc/users/external-data-sources.md#prip-stations)). |
| [Catalog](https://rspy.ops.rs-python.eu/docs#/Catalog) | `/catalog/...` | Read and update the catalog ([documentation](../rs-server/docs/doc/users/catalog.md)). |
| [Staging service](https://rspy.ops.rs-python.eu/docs#/Staging%20service) | `/processes`, `/jobs` | Stage products into the catalog and follow the staging jobs ([documentation](../rs-server/docs/doc/users/staging.md)). |
| [Processing service](https://rspy.ops.rs-python.eu/docs#/Processing%20service) | `/dpr/processes`, `/dpr/jobs` | Read the processors task tables and follow or cancel the DPR jobs ([documentation](../rs-dpr-service/docs/doc/index.md)). |
| [OSAM service](https://rspy.ops.rs-python.eu/docs#/OSAM%20service) | `/storage/...` | Get your S3 credentials; synchronise the object storage accounts (administrators only) ([documentation](../rs-server/docs/doc/users/osam.md)). |
| Authentication | `/auth/me` | Show your user name and roles. |

The required rights for each endpoint are listed in [Endpoints and permissions](../annexes/endpoints.md).

## Log in

1. Click the *Login* link at the top of the page and log in with your Keycloak account. You are now
   authenticated with an OAuth2 session cookie. Alternatively, click one of the lock icons and enter your
   [API key](../getting-started/user-rights.md#api-keys).
2. To check that you are logged in, expand the `GET /auth/me` endpoint, click *Try it out* then *Execute*: the
   response shows your user name and your roles.

## Examples

### Search a station

1. Expand `GET /cadip/collections` and execute it: the response lists the CADIP collections you can read.
2. Expand `GET /cadip/collections/{collection_id}/items`, enter one of the collection identifiers, e.g. `sgs`, and
   a `datetime` interval, then execute it: the response is a STAC `FeatureCollection` of sessions.
3. Expand `GET /cadip/collections/{collection_id}/items/{session_id}` and enter one of the session identifiers to
   read its details.

You can also copy the request URL displayed by Swagger, e.g. `https://rspy.ops.rs-python.eu/cadip/collections/sgs/items`,
into your browser address bar: as you are logged in, you can then click on the links of the JSON responses to
navigate between the collections and the items. The [STAC browsers](browse-products.md#stac-browsers) offer a more
user-friendly interface for the same purpose.

### Search the catalog

Execute `GET /catalog/collections` to list the collections you can read. The first time, the list may be empty:
your collections are created when you stage or process products. See [Browse products](browse-products.md) for the
search parameters.

### Get your S3 credentials

Execute `GET /storage/account/credentials` to get your personal object storage credentials, then use them as
described in [Download the assets](browse-products.md#download-the-assets).

### Follow a job

The staging and processing jobs are usually started by the Prefect flows. To follow a job, execute
`GET /jobs/{job_id}` (staging) or `GET /dpr/jobs/{job_id}` (processing) with the job identifier written in the flow
logs. A DPR job can be cancelled with `DELETE /dpr/jobs/{job_id}`, see
[Cancel a DPR run](../rs-dpr-service/docs/doc/cancel-dpr-run.md).

## Call an endpoint with your API key

Outside of the Swagger page, pass your API key in the `x-api-key` HTTP header, e.g.:

```shell
curl -H "x-api-key: <your-api-key>" "https://rspy.ops.rs-python.eu/catalog/collections"
```
