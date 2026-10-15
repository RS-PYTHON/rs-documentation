# Set up your environment

The Prefect flows run on the cluster, on behalf of a user. To do so, they read the information they need (service
URLs, API key, object storage credentials...) from [Prefect secret blocks](https://docs.prefect.io/v3/concepts/blocks):

| Prefect block | Content | Created by |
|---|---|---|
| `env-vars` | Environment variables shared by all the users of the Prefect instance: service URLs, Dask Gateway address and token, temporary bucket, monitoring database... | An administrator, once, see [Initialise the processing environment](../administration/init-processing-environment.md). |
| `env-vars-<your-login>` | Your own environment variables: your API key (`RSPY_APIKEY`) and your object storage credentials (`S3_ACCESSKEY`, `S3_SECRETKEY`, `S3_ENDPOINT`, `S3_REGION`). | You, as described below. |

Each flow receives your user name as the `owner_id` parameter (inside the `env` parameter of most flows) and reads
these two blocks before calling the services. See [Authentication](../rs-client-libraries/docs/doc/flows/authentication.md)
for the details.

## Prerequisites

- You have an account on the platform with access to [JupyterHub](../services/virtual-environment/jupyterhub.md),
  e.g. <https://processing.ops.rs-python.eu/jupyter>, and to [Prefect](../services/virtual-environment/prefect.md),
  e.g. <https://processing.ops.rs-python.eu/dashboard>.
- You have [created an API key](user-rights.md#api-keys).
- Your administrator has initialised the `env-vars` block. To check it, open the *Blocks* page of the Prefect
  dashboard: it must contain a `env-vars` secret block.
- The Dask clusters needed by the flows you want to run are started, see
  [Add and delete Dask clusters](../rs-workflow-env/docs/dask-clusters.md).

## Initialise your Prefect block

Open a JupyterHub session, create a new notebook and run:

```python
import os
from rs_client.rs_client import RsClient
from rs_common.prefect_utils import init_prefect_blocks, save_bucket_credentials

# Create or update the "env-vars-<your-login>" Prefect block with your API key.
# If the API key is not already saved in your "~/.env" file, you are asked to enter it,
# then it is saved in "~/.env" for the next times.
await init_prefect_blocks()

# Get your object storage (S3) credentials from the OSAM service and save them in the same block
rs_client = RsClient(os.environ["RSPY_WEBSITE"], os.environ["RSPY_APIKEY"])
await save_bucket_credentials(rs_client.get_osam_client())
```

!!! note

    In JupyterHub, the `RSPY_*` environment variables needed to call the services are already set, and the
    [rs-client-libraries](../rs-client-libraries/docs/doc/index.md) are already installed.
    Outside a notebook (i.e. without a running asyncio event loop), call the same functions with the `_sync=True`
    argument, e.g. `init_prefect_blocks(_sync=True)`.

Your block is now visible in the *Blocks* page of the Prefect dashboard, as `env-vars-<your-login>`. You can also
check its content from a JupyterHub terminal:

```shell
prefect block ls
prefect block inspect secret/env-vars-<your-login>
```

Run these commands again when your API key is renewed or replaced.

!!! warning "Don't store your OAuth2 session cookie in Prefect"

    The OAuth2 session cookie has a short lifespan, so the flows would fail as soon as it expires. Always use an
    API key to run the Prefect flows.

## Next step

[Run existing flows](run-existing-flows.md).
