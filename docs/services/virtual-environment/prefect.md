# Prefect

[Prefect](https://www.prefect.io/) is the open-source workflow orchestration tool used by RS-Python to implement,
run, schedule, chain and monitor the processing workflows. It offers:

- **workflows as Python code**: a flow is a Python function decorated with `@flow`, that calls tasks (`@task`) and
  other flows (see [Write and run flows](https://docs.prefect.io/v3/how-to-guides/workflows/write-and-run)),
- **parameterised runs**: the flow parameters are typed and can be set at runtime from the dashboard or from code,
- **resilience**: retries, timeouts, caching, concurrency limits,
- **automation**: schedules, and automations that start flows when an event occurs,
- **observability**: logs, states and artifacts of each run in a web dashboard.

## Prefect dashboard

The Prefect dashboard of your group, e.g. <https://processing.ops.rs-python.eu/dashboard> on the reference
platform, shows:

| Page | Content |
|---|---|
| *Runs* | The flow runs, their state, logs, parameters, sub-flows, tasks and [artifacts](https://docs.prefect.io/v3/concepts/artifacts). |
| *Flows* and *Deployments* | The flows available on the platform and their deployments, that you can run with *Quick run* or *Custom run* (see [Run existing flows](../../getting-started/run-existing-flows.md)). |
| *Work pools* | The work pools and their workers, see below. |
| *Blocks* | The [secret blocks](https://docs.prefect.io/v3/concepts/blocks) with the environment variables of the platform and of the users (see [Set up your environment](../../getting-started/setup-environment.md)). |
| *Variables* | The [variables](https://docs.prefect.io/v3/concepts/variables) with the default settings of the flows (see [Customise the DPR processing](../../rs-client-libraries/docs/doc/advanced/customise-dpr-flow.md)). |
| *Automations* | The automations that chain the flows (see [Systematic processing](../../rs-client-libraries/docs/doc/advanced/systematic-processing.md)). |

The [Prefect UI documentation](https://docs.prefect.io/v3/get-started) describes all the features.

## Deployments

A [deployment](https://docs.prefect.io/v3/concepts/deployments) makes a flow runnable from the dashboard, from an
automation or from another flow, on the platform workers. Deployments are named `<flow-name>/<deployment-name>`,
e.g. `process-l0/Process L0`, and tagged by kind of processing (`staging`, `processing`, `searching`,
`operation`...), mission (`s1`, `s3`...) and level (`l0`, `l1`...) to ease the search. The deployments delivered by
default are listed in [Prefect flows](../../rs-client-libraries/docs/doc/flows/index.md#deployments) and deployed by
[rs-workflow-deployment](../../rs-workflow-deployment/README.md).

## Work pools

The flow runs of the deployments are executed by [Prefect workers](https://docs.prefect.io/v3/concepts/workers),
that create one Kubernetes pod per flow run. They are organised in [work pools](https://docs.prefect.io/v3/concepts/work-pools):

| Work pool (default name) | Usage |
|---|---|
| `processing-integrated-k8s-pool` | The searching, staging and processing flows delivered by default with RS-Python. |
| `processing-sandbox-k8s-pool` | The custom flows developed and deployed by the users. |
| `monitoring-k8s-pool` | The operation flows: OSAM synchronisation, object storage quota monitoring, cleaning. |

Their names are given by the `PREFECT_WORK_POOL_INTEGRATED`, `PREFECT_WORK_POOL_SANDBOX` and
`PREFECT_WORK_POOL_MONITORING` environment variables in [JupyterHub](jupyterhub.md). The administrators can set
concurrency limits on the work pools, see [Prefect work pools](../../rs-infra-core/docs/how-to/prefect-work-pools.md).

## Authentication

The flows always authenticate to the RS-Python services with the API key of the user, never with the OAuth2
cookie that has a short lifespan. See [Authentication](../../rs-client-libraries/docs/doc/flows/authentication.md).
