# Initialise the processing environment

After the deployment of the platform, and for each new user group (each Prefect instance), the administrators
initialise the shared processing environment. The [rs-demo](https://github.com/RS-PYTHON/rs-demo) repository
provides Jupyter notebooks for these tasks: clone it in your [JupyterHub](../services/virtual-environment/jupyterhub.md)
session and run them from there.

## 1. Prefect block `env-vars`

The `env-vars` [Prefect secret block](https://docs.prefect.io/v3/concepts/blocks) contains the environment
variables shared by all the users of the Prefect instance. The flows read it at startup (see
[Authentication](../rs-client-libraries/docs/doc/flows/authentication.md)). Initialise it with the
[`notebooks/init-prefect/env-vars.ipynb`](https://github.com/RS-PYTHON/rs-demo/blob/develop/notebooks/init-prefect/env-vars.ipynb)
notebook, that copies the values of the JupyterHub environment and asks for the others:

| Variable | Description |
|---|---|
| `RSPY_WEBSITE`, `RSPY_UAC_CHECK_URL`, `RSPY_PREFECT_URL` | URLs of the RS-Python services, of the API Key Manager and of Prefect (copied from JupyterHub). |
| `DASK_GATEWAY_ADDRESS`, `DASK_GATEWAY_PUBLIC` | Internal and public addresses of the Dask Gateway (copied from JupyterHub). |
| `JUPYTERHUB_API_TOKEN` | Token used by the flows and the services to connect to the Dask clusters (Dask Gateway uses the [JupyterHub authentication](https://gateway.dask.org/authentication.html#using-jupyterhub-s-authentication)). |
| `TEMPO_ENDPOINT` | OpenTelemetry endpoint for the traces (copied from JupyterHub). |
| `PREFECT_BUCKET_NAME`, `PREFECT_BUCKET_FOLDER` | Temporary bucket and folder used by the flows to share files, e.g. the payload files of the processors. |
| `POSTGRES_HOST`, `POSTGRES_PORT`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_PI_DB` | Connection to the [performance indicators](../rs-client-libraries/docs/doc/operation/performance-indicators.md) database (from the `rs_performance_indicator` inventory variables). |
| `RSPY_HOST_OSAM` | Internal URL of the OSAM service. |

Each user then creates their own `env-vars-<login>` block, see
[Set up your environment](../getting-started/setup-environment.md). The processing flows delivered by default run
on behalf of a technical owner (e.g. `copernicus`): create its account and its block the same way.

## 2. Prefect variables

The [Prefect variables](https://docs.prefect.io/v3/concepts/variables) contain the default settings of the flows:

| Variable | Content | Documentation |
|---|---|---|
| `processing-storage-configuration` | Where the processors read and write their inputs, outputs and auxiliary files (S3 buckets, shared disks...). Initialise it with the [`notebooks/init-prefect/processing-storage-configuration.ipynb`](https://github.com/RS-PYTHON/rs-demo/blob/develop/notebooks/init-prefect/processing-storage-configuration.ipynb) notebook, from the [template](https://github.com/RS-PYTHON/rs-client-libraries/blob/develop/config/storage_configuration.json) delivered with rs-client-libraries. | [Storage configuration](../rs-client-libraries/docs/doc/advanced/customise-dpr-flow.md#storage-configuration) |
| `s<mission>-processing-default-setting` | Default parameters of the processing flows of a mission: processor, pipeline, Dask cluster, target collections... | [Customise the DPR processing](../rs-client-libraries/docs/doc/advanced/customise-dpr-flow.md#default-settings-of-the-processing-flows) |

## 3. Dask clusters

Start the Dask clusters needed by the flows, see [Add and delete Dask clusters](../rs-workflow-env/docs/dask-clusters.md).
The staging Dask cluster is kept running automatically by the `dask-cluster-staging` application of
[rs-server-deployment](../rs-server-deployment/README.md).

## 4. Flows and automations

The flows and automations delivered by default are deployed by
[rs-workflow-deployment](../rs-workflow-deployment/README.md). Check that they are visible in the *Deployments*
and *Automations* pages of the Prefect dashboard.

## 5. Users

[Create the user accounts and assign their permissions](accounts-permissions.md), then run the OSAM
synchronisation.
