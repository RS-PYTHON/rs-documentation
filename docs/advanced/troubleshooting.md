# Troubleshooting

This page lists the tools to investigate a failed or slow flow run, and the most common errors.

## Tools

| Tool | What you find there |
|---|---|
| [Prefect dashboard](../services/virtual-environment/prefect.md) | The state, logs, parameters and artifacts of each flow run and task run. Start your investigation here. The processing flows publish the processor task table (`dpr-task-table` artifact) and payload file (`dpr-payload` artifact). |
| [Dask dashboard](../services/virtual-environment/dask.md) | The tasks in progress, CPU and memory of each worker of a Dask cluster. Its URL is written in the logs of the processing flows. |
| [Swagger](../services/swagger.md) | The status of the staging (`GET /jobs/{job_id}`) and processing (`GET /dpr/jobs/{job_id}`) jobs, your rights (`GET /auth/me`). |
| [Grafana](../administration/monitoring.md) | The logs of all the pods ([Loki](https://grafana.com/oss/loki/)), the traces of the requests between the flows, the services and the Dask workers ([Tempo](https://grafana.com/oss/tempo/)), and the resources consumption of the pods ([Prometheus](https://prometheus.io/)). Reserved to administrators and operators. |

### Follow a request across the components

All the components are instrumented with [OpenTelemetry](https://opentelemetry.io/): the trace context is
propagated from the Prefect flow to the rs-server services, to rs-dpr-service and to the Dask workers that run the
processors. In Grafana, open the *Explore* page with the Tempo data source and search the traces by service name
(e.g. `rs.workflows`, `rs.server.staging`) or by time range to see the whole chain of calls of a flow run, and
their durations.

### Check the resources consumed by a processor

In Grafana, open the *Kubernetes / Views / Pods* dashboard, select the `dask-gateway` namespace and look at the
*CPU Usage by container* and *Memory Usage by container* panels during the processor run.

## Common errors

| Symptom | Cause and solution |
|---|---|
| `401` error with `Missing authorization role 'rs_...' for user ...` | You don't have the right to access this station, collection or process. Check your roles with `/auth/me` and ask your administrator for the missing role, see [User rights](../getting-started/user-rights.md#available-rights). |
| `401` or `403` error when calling the services from a flow | Your API key has expired, has been revoked, or is not the one saved in your Prefect block. Renew it with the API Key Manager and [update your Prefect block](../getting-started/setup-environment.md). |
| `ValueError: Unable to find block document named env-vars...` | The `env-vars` block (created by an administrator) or your `env-vars-<login>` block is missing, see [Set up your environment](../getting-started/setup-environment.md). |
| `'<label>' is unknown or not ready` | The Dask cluster with this label is not running, see [Add and delete Dask clusters](../rs-workflow-env/docs/dask-clusters.md). |
| Errors about incompatible versions when connecting to a Dask cluster | The Dask client (notebook kernel, rs-dpr-service image) and the Dask cluster must use the same Python and Dask versions, see [Dask images](../rs-workflow-env/docs/dask_images.md). |
| Dask workers restarted, `KilledWorker` errors | The processor needs more memory than available on the workers. Use a cluster with bigger workers. |
| `Access Denied` when reading or writing the object storage | Your S3 credentials are missing from your Prefect block, or your object storage rights are not synchronised yet with your Keycloak roles. Save your credentials again and ask your administrator to run the [OSAM synchronisation](../rs-server/docs/doc/users/osam.md). |
| No auxiliary file found by the processing | The auxiliary files required by the [task table](../rs-client-libraries/docs/doc/flows/tasktable-payload.md) are not available in the configured source. Check the `auxiliary_product_to_collection_identifier` parameter and the time interval of the input products. |
| A flow stays in the *Pending* or *Late* state | No Prefect worker is available in its work pool, or the work pool concurrency limit is reached. Contact your administrator. |

If you can't solve the issue, contact your platform administrator with the flow run URL and the time of the
error. For a bug in RS-Python, open an issue in the relevant
[GitHub repository](../getting-started/project-organisation.md#source-code-organisation).
