# JupyterHub

[JupyterHub](https://jupyter.org/hub) gives you a personal [JupyterLab](https://jupyterlab.readthedocs.io/)
session running on the cluster, e.g. <https://processing.ops.rs-python.eu/jupyter> on the reference platform. Log in
with your Keycloak account (you need to be a member of the JupyterHub users group, see
[User rights](../../getting-started/user-rights.md#applications)).

JupyterLab combines in a single web interface notebooks, a text editor, a terminal and a file browser, with
flexible layouts and support for many file formats. See the
[JupyterLab user guide](https://jupyterlab.readthedocs.io/en/stable/user/interface.html).

## What is already set up for you

- The latest [rs-client-libraries](../../rs-client-libraries/docs/doc/index.md) and their dependencies
  ([Prefect](https://www.prefect.io/), [Dask Gateway](https://gateway.dask.org/),
  [pystac-client](https://pystac-client.readthedocs.io/)...) are installed. Check the version with
  `pip show rs-client-libraries` from a terminal.
- The environment variables needed to call the services are set, e.g.:

    | Variable | Description |
    |---|---|
    | `RSPY_WEBSITE` | URL of the RS-Python web services. |
    | `RSPY_UAC_HOMEPAGE`, `RSPY_UAC_CHECK_URL` | URLs of the API Key Manager. |
    | `PREFECT_API_URL` | URL of the Prefect server of your group. |
    | `PREFECT_WORK_POOL_INTEGRATED`, `PREFECT_WORK_POOL_SANDBOX`, `PREFECT_WORK_POOL_MONITORING` | Names of the Prefect work pools, see [Prefect](prefect.md#work-pools). |
    | `DASK_GATEWAY_ADDRESS`, `DASK_GATEWAY_PUBLIC` | Internal and public addresses of the Dask Gateway. |
    | `S3_ENDPOINT`, `S3_REGION` | Object storage endpoint. |
    | `TEMPO_ENDPOINT` | OpenTelemetry endpoint for the traces. |

- The variables that you write in the `~/.env` file of your home directory are loaded automatically when a
  notebook kernel starts. This is where your API key is saved as `RSPY_APIKEY` (see
  [Set up your environment](../../getting-started/setup-environment.md)).
- Additional Jupyter kernels, one per Python and Dask version used by the Dask clusters, are available: a Dask
  client must use the same Python and Dask versions as the cluster it connects to (see
  [Dask images](../../rs-workflow-env/docs/dask_images.md)).

Your home directory, `/home/rspy`, is persistent: your files are kept when your session is stopped.

## Demo notebooks

The [rs-demo](../../rs-demo/README.md) repository contains notebooks that show how to use the services, the
libraries and the flows. Clone it in your home directory, from a JupyterHub terminal:

```shell
git clone https://github.com/RS-PYTHON/rs-demo.git
```

Most of the demos start by calling `init_demo()` from `rs-demo/notebooks/resources/utils.py`, that initialises
your Prefect block, an `RsClient` instance and your object storage credentials.

## Use another rs-client-libraries version

To test a version of the [rs-client-libraries](../../rs-client-libraries/docs/doc/index.md) that is not yet
installed in the JupyterHub image (e.g. a development branch), either:

- install its wheel package for your user only. Download it from the `Artifacts` section of the
  [publish workflow](https://github.com/RS-PYTHON/rs-client-libraries/actions/workflows/publish-binaries.yml)
  run of your branch, or build it with `poetry build --format wheel`, upload it to your session, then from a
  terminal:

    ```shell
    pip install --user rs_client_libraries-<version>-py3-none-any.whl
    opentelemetry-bootstrap -a install
    ```

- or clone the repository and add it to the Python path of your notebook:

    ```python
    import sys
    sys.path.insert(0, "/home/rspy/rs-client-libraries")  # path of your clone
    import rs_client
    print(rs_client.__path__)
    ```

To update the version installed for everyone, ask your administrator to deploy a new JupyterHub image (built by
the [rs-workflow-env](../../rs-workflow-env/README.md) CI/CD).
