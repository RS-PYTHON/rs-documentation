# Running a DPR processor on a Dask cluster: architecture review

This page explains how a DPR processor is run on a [Dask](https://www.dask.org/) cluster, analyses the strengths and
weaknesses of the current design, and proposes a better one, with its impact on the infrastructure. It is written
for the developers and the infrastructure operators of RS-Python, and the first sections are meant for beginners.

!!! info "Status"

    Sections 1 to 4 describe the system **as implemented today**, checked against the source code of
    [rs-dpr-service](https://github.com/RS-PYTHON/rs-dpr-service),
    [rs-demo](https://github.com/RS-PYTHON/rs-demo) and [EOPF-CPM](https://cpm.pages.eopf.copernicus.eu/eopf-cpm/main/index.html).
    Sections 5 to 8 are an **architecture proposal**, not yet implemented. The points that could not be verified from
    the code are listed in [Assumptions to verify](#assumptions-to-verify).

## 1. Vocabulary for beginners

| Term | Meaning |
|---|---|
| **Processor** | A scientific program (e.g. Sentinel-1 level-1 processing) written with EOPF-CPM. It reads input products and writes output products. |
| **EOPF-CPM** | *Earth Observation Processing Framework - Core Python Modules*. The library that runs a processor from a *payload file* (command `eopf trigger local payload.yaml`). |
| **Payload file** | A YAML file that describes a run: inputs, outputs, parameters, and how to connect to Dask (the `context_managers` field). |
| **Dask** | A Python library that splits a computation into many small **tasks** and runs them in parallel. |
| **Scheduler** | The Dask component that receives the tasks and distributes them to the workers. |
| **Worker** | A Dask process (here a Kubernetes pod) that executes the tasks. It has a number of **threads**: one thread runs one task at a time. |
| **Dask cluster** | One scheduler plus several workers, all started from the same Docker image. |
| **Dask Gateway** | The service that creates, lists and stops the Dask clusters on Kubernetes. |
| **Cluster id / label** | The *id* (e.g. `dask-gateway.17e196...`) identifies one running cluster. The *label* (e.g. `dask-cpm3`) is a human-readable name. |
| **Client** | Any program that submits tasks to a cluster (a notebook, rs-dpr-service, EOPF-CPM...). |
| **Prefect flow** | A Python workflow, started from the Prefect dashboard, that orchestrates a processing. |
| **rs-dpr-service** | The REST service ([OGC API - Processes](https://ogcapi.ogc.org/processes/)) that runs the processors. See [DPR processors](../rs-dpr-service/docs/doc/index.md). |

## 2. Overview

![Overview](../images/dask-processing-overview.svg)

Four building blocks cooperate:

1. The **user's notebook** creates a Dask cluster with Dask Gateway.
2. A **Prefect flow** ([rs-client-libraries](https://github.com/RS-PYTHON/rs-client-libraries)) gathers the user's
   inputs and writes the payload file.
3. **rs-dpr-service** receives a REST call, completes the payload and runs the processor.
4. The **Dask cluster** executes the processor, next to the object storage (S3) that contains the products.

## 3. How it works today

The user first creates a cluster with one of the notebooks of
[rs-demo/notebooks/init-dask-clusters](https://github.com/RS-PYTHON/rs-demo/tree/develop/notebooks/init-dask-clusters)
(one notebook per processor family: `cpm3`, `l0`, `s1ard`, `s3olci`, `mockup`, `staging`). See also
[Add and delete Dask clusters](../rs-workflow-env/docs/dask-clusters.md). The notebook starts the cluster from a
Docker image, then prints its **instance id** and its **label**.

![Current sequence](../images/dask-processing-current-sequence.svg)

| # | Who | What |
|---|---|---|
| 1 | User, notebook | Creates the Dask cluster and gets its id and label. The notebook must run in a kernel whose Python and Dask versions match the cluster image (it checks it with `assert`). |
| 2 | Prefect flow | Reads the user's input (including the cluster id and label) and writes the payload file. |
| 3 | Prefect flow | Calls rs-dpr-service with a REST request `POST /processes/{processor}/execution` and the payload. |
| 4 | rs-dpr-service | Completes the payload, in particular the `context_managers` field. It contains the `reuse_cluster` parameter set to the cluster id of step 1 (see [`write_dask_context`](https://github.com/RS-PYTHON/rs-dpr-service/blob/develop/rs_dpr_service/dask/call_dask.py)). |
| 5 | rs-dpr-service | Connects to the cluster through Dask Gateway and submits **task #1**: `ProcessorCaller.run_processor`. |
| 6 | Task #1 (in a worker) | Downloads the configuration from S3, then starts the EOPF-CPM job in a subprocess: `eopf_otel trigger local payload.yaml`. It streams the logs and handles the cancellation (Dask event). |
| 7 | EOPF-CPM | Reads `context_managers`, connects to the **same cluster** thanks to `reuse_cluster`, and submits **task #2**: the actual computation of the processor, split into many Dask tasks. |

### Why one rs-dpr-service instance per processor family

![Version coupling](../images/dask-processing-version-coupling.svg)

The processors do not all use the same Python and Dask versions. A Dask client and its cluster must use compatible
versions, so rs-dpr-service, which is a Dask client in step 5, must have **the same Python and Dask versions as the
processor**. It is the reason why several instances of rs-dpr-service are deployed in the `processing` namespace
(see [rs-server-deployment/apps](https://github.com/RS-PYTHON/rs-server-deployment/tree/develop/apps), e.g.
`rs-dpr-service-py-3-11-7-dask-2024-5-2`, `rs-dpr-service-py-3-11-7-dask-2026-1-2` and
`rs-dpr-service-py-3-13-16-dask-2026-3-0`), and why the gateway routes each processor to the right instance.

The same constraint applies to the notebook kernel that creates the cluster.

## 4. Assessment of the current method

The method nests two levels of Dask tasks on the same cluster: task #1 (the "launcher") starts EOPF-CPM, which
submits task #2 (the computation) to the same workers.

### Pros

| Pro | Explanation |
|---|---|
| **No new component** | Everything goes through Dask Gateway and the existing clusters. rs-dpr-service needs no Kubernetes permission. |
| **Right environment by construction for EOPF-CPM** | The EOPF-CPM driver runs inside a pod created from the cluster image, so its Python, Dask and processor versions are exactly those of the cluster. |
| **Driver close to the data and the scheduler** | The EOPF-CPM driver talks to the scheduler from inside the Kubernetes network, with a low latency and no long-lived connection through the gateway. |
| **Cancellation and log streaming already work** | A Dask `Event` stops the subprocess, and the logs are forwarded to rs-dpr-service and Prefect (see [Cancel a DPR run](../rs-dpr-service/docs/doc/cancel-dpr-run.md)). |
| **Quotas are enforced in one place** | The cluster options (`cluster_max_workers`, `cluster_max_cores`, `cluster_max_memory`) cap what a run can consume. |
| **Simple to operate on small setups** | One cluster, one service, no job controller. |

### Cons

| Con | Explanation | Severity |
|---|---|---|
| **Thread starvation, possible deadlock** | Task #1 only waits for task #2 but occupies a worker thread during the whole run. If *N* runs share a cluster with at most *N* threads (e.g. 3 concurrent runs on one worker of 3 cores), no thread is left for any task #2: the runs hang without failing. See the diagram below. | High |
| **Wasted capacity** | Every run permanently wastes one thread of a worker, and workers are billed on-demand nodes. | Medium |
| **The driver competes with the computation** | The EOPF-CPM subprocess (graph construction, logging, S3 transfers of the configuration) shares the CPU and the RAM limit of a worker pod with the tasks. An out-of-memory kill of the pod kills the driver and the computation together. | High |
| **A worker failure can replay the whole run** | Dask reschedules the tasks of a lost worker (`distributed.scheduler.allowed-failures`, 3 by default). Task #1 is the whole processor run, so it may be started again with its side effects (outputs written twice). | Medium |
| **Version coupling** | rs-dpr-service must match the Python and Dask versions of each processor, hence one Deployment, Helm values, route and CI build per version. Adding a processor with a new Python or Dask version means deploying a new instance. | High |
| **Secrets travel through Dask** | The JupyterHub API token and the S3 credentials are put in the serialized task, so they pass through the scheduler. | Medium |
| **Harder to observe and debug** | A failure can be in the REST service, in task #1, in the subprocess or in task #2. Task #1 shows as a long task in the Dask dashboard that is not real work. | Low |
| **Opaque lifecycle** | A run is a Python task, not a Kubernetes object: no `kubectl get jobs`, no TTL, no native deadline. | Low |

![Thread starvation](../images/dask-processing-thread-starvation.svg)

**Conclusion.** The idea is not wrong: running the driver next to the scheduler, from the cluster image, is sound.
The weakness is *where* the driver runs. Putting it in a Dask task makes it consume the resources it is supposed to
orchestrate, and keeps rs-dpr-service tied to the Dask version. The nested task is what turns a performance
inefficiency into a risk of deadlock.

## 5. Options

| Option | Description | Removes nested tasks | Removes version coupling | Infrastructure change | Effort |
|---|---|---|---|---|---|
| **A. Keep as is** | Reference. | No | No | None | None |
| **B. Mitigate in place** | Keep the design. Call [`secede()`](https://distributed.dask.org/en/stable/task-launch.html) at the start of task #1 so it releases its thread while it waits, and/or start the workers with more threads than cores, and/or use one cluster per run. | Partly (no more deadlock, still two levels) | No | None | Small |
| **C. Driver in rs-dpr-service** | rs-dpr-service runs `eopf trigger` itself (subprocess in its own pod); EOPF-CPM connects to the cluster. No task #1. | Yes | No (EOPF-CPM must be installed in each instance, with the right versions) | Bigger pods | Medium |
| **D. One Kubernetes Job per run (recommended)** | rs-dpr-service creates a short-lived Kubernetes Job from the **cluster image**. The Job runs `eopf trigger`, which connects to the existing cluster. | Yes | **Yes**: a single generic rs-dpr-service | New RBAC, driver pods | Medium |
| **E. Prefect-native** | The Prefect flow itself starts the Kubernetes Job (Prefect Kubernetes work pool), and rs-dpr-service disappears or only keeps the catalogue of processors. | Yes | Yes | Prefect work pool | Large (changes the public API) |

**Why not C.** It removes the nested task but concentrates the drivers of all runs in the service pods (memory,
concurrency, cancellation by signals, no isolation between users' runs), and it keeps EOPF-CPM, Python and Dask in
each rs-dpr-service image: the version coupling remains.

**Why not E now.** It is the cleanest long-term target, but it removes the OGC API - Processes interface and
changes all the clients. Option D can be done first, and is a step toward E.

## 6. Recommended design: a driver Job per run

The EOPF-CPM driver moves out of the Dask cluster, into a Kubernetes Job created from **the same image as the
cluster**. Dask then only runs the computation.

![Proposed sequence](../images/dask-processing-proposed-sequence.svg)

| Step | Change compared to today |
|---|---|
| 1 to 3 | Unchanged: cluster creation, payload file, REST call. |
| 4 | rs-dpr-service completes the payload as before (`reuse_cluster`) and reads the **image of the cluster** from Dask Gateway (`options["image"]` of the cluster report, which the init notebooks already use to find clusters). The processor name is no longer needed to choose an image. |
| 5 | rs-dpr-service creates a Kubernetes `Job` (one pod, `restartPolicy: Never`, `backoffLimit: 0`) with that image. The payload location, the S3 settings and the OpenTelemetry trace context are passed as environment variables, the JupyterHub token in a per-run `Secret` owned by the Job. |
| 6 | The driver pod downloads the configuration and runs `eopf_otel trigger local payload.yaml`: it is the code of `ProcessorCaller.init`/`trigger` of today, packaged as a small runner that works with Python 3.11 to 3.13. |
| 7 | EOPF-CPM connects to the existing cluster (`reuse_cluster`) and submits its tasks. These are the **only** Dask tasks. |
| Logs and status | rs-dpr-service reads the pod logs and the Job status with the Kubernetes API (the logs are also collected by Alloy and Loki), and exposes them as today to the Prefect flow. |
| Cancellation | rs-dpr-service deletes the Job. The pod receives a SIGTERM, which EOPF-CPM already handles; the termination grace period replaces the `time.sleep(60)` followed by SIGKILL. |

### What is gained

- **No nested tasks**: all the threads of the workers compute. No thread starvation and no deadlock.
- **The driver is isolated**: its memory is accounted and limited by its own pod, it does not compete with the
  computation, and its crash does not kill a worker.
- **One generic rs-dpr-service**: it no longer submits Python code to the cluster, so it no longer depends on the
  Python and Dask versions of the processors. The Python and Dask versions are chosen by the cluster image, which is
  used for both the driver and the workers. Adding a processor requires **no new service instance**.
- **No replay of a whole run** by Dask after a worker loss: a failed driver is a failed Job (`backoffLimit: 0`),
  retried only if the user decides so.
- **Clear lifecycle**: `activeDeadlineSeconds`, `ttlSecondsAfterFinished`, Job metrics (if kube-state-metrics is
  deployed), Kubernetes events.
- **Smaller attack surface for the secrets**: no more credentials in the serialized tasks.

### What it costs

- **A start-up delay** of the driver pod (scheduling plus image pull). It is limited if the node already has the
  image (see the node pools below).
- **A new privilege** for rs-dpr-service: creating Jobs in its namespace.
- **A packaging work**: the runner code (today `call_dask.py`, uploaded to the workers as a zip) must be available in
  the driver pod, either baked in the Dask images built by
  [rs-workflow-env](https://github.com/RS-PYTHON/rs-workflow-env) or copied by an init container.
- **A change in the status handling**: the state of a run comes from the Kubernetes Job instead of the Dask future.

## 7. Impact on the infrastructure

![Infrastructure impact](../images/dask-processing-infrastructure-impact.svg)

| Area | Today | Proposed | Action |
|---|---|---|---|
| **rs-dpr-service Deployments** | One per Python/Dask version (3 today) | One generic Deployment (replicas for availability, not for versions) | Merge the `rs-dpr-service-py-*` applications of [rs-server-deployment](https://github.com/RS-PYTHON/rs-server-deployment), keep the old ones during the migration. |
| **Routing (Envoy Gateway)** | One route per processor to the right instance | A single route | Simplify the routes and the Helm values. |
| **CI/CD and images** | One rs-dpr-service image per Python/Dask version | One image, plus the runner packaged in the Dask images | Update the [publish workflow](ci-cd.md) and the [Dask images](../rs-workflow-env/docs/dask_images.md) build. |
| **RBAC** | None | `ServiceAccount` and `Role` in the namespace of the Jobs: `create`, `get`, `list`, `watch`, `delete` on `jobs`; `create` on `secrets` (no `get` or `list`); `get`, `list` on `pods` and `pods/log`. | Add to the [rs-helm](https://github.com/RS-PYTHON/rs-helm) chart. Restrict to the namespace and to the Jobs labelled by the service. |
| **Node pools** | Drivers run in the `dask_worker_on_demand` pool, inside the workers | Driver pods need a place to run | See the sizing note below. |
| **Quotas** | Cluster options limit the workers | The driver pods must also be bounded | `ResourceQuota` and `LimitRange` on the namespace in which the Jobs run; `requests` and `limits` set on each Job. |
| **Network policies** | rs-dpr-service reaches Dask Gateway | The driver pod also reaches Dask Gateway (and the scheduler through it), S3 and the OpenTelemetry endpoint | Add the egress rules for the driver pods label. |
| **Secrets** | The JupyterHub token travels in the Dask task | One short-lived `Secret` per run, owned by the Job (deleted with it) | Mount the secret as an environment variable of the driver pod. |
| **Observability** | Logs of the service and of the workers | Logs of the driver pod, Job metrics | Add the Job dashboards in [rs-infra-monitoring](https://github.com/RS-PYTHON/rs-infra-monitoring); keep the trace context propagation (`TRACEPARENT`) which already works with a subprocess. |
| **Dask clusters** | `scale` workers, one of which is partly used by the drivers | The same cluster, with all threads available to the computation | Optionally reduce the size of the clusters, which are no longer penalised by the drivers. |
| **Cost** | Constant | A few short-lived small pods, fewer always-on service pods | Neutral to slightly positive. |

**Sizing note.** The init notebooks report that a worker node offers at most 3 CPU and 12 GB RAM, and that the
scheduler node offers at most 7 CPU and 58 GB RAM with the scheduler taking most of it by default. A driver pod needs
a modest request (to be measured: start with 1 CPU and 2 to 4 GB) and the image of the cluster, which is large. Two
possibilities:

1. Add a small **driver node pool** (a few nodes, scale to zero or to one) and pre-pull the Dask images with a
   DaemonSet or an image cache, to keep the start-up delay low.
2. Schedule the drivers on the scheduler node pool, which already has the image, provided the scheduler memory
   request is reduced to leave room.

Option 1 is preferred because it isolates the drivers from the scheduler.

## 8. Migration plan

| Phase | Content | Exit criterion |
|---|---|---|
| **0. Measure and secure** | Check the number of threads per worker, reproduce the starvation with *N* concurrent runs on a small cluster, apply option B (`secede()`, or document one run per cluster) as a safety net. | The deadlock is reproduced and then no longer occurs. |
| **1. Proof of concept** | Package the runner, create the Job by hand with the `cpm3` image, run an existing payload. Measure the driver memory and start-up delay. | A full run succeeds with the driver outside the cluster; sizing values are known. |
| **2. Service integration** | Add an `execution_mode` setting (`dask_task` or `k8s_job`) in rs-dpr-service. Implement Job creation, logs, status, cancellation, cleanup, RBAC. Keep the current mode as default. | The existing tests and the [rs-demo](https://github.com/RS-PYTHON/rs-demo) notebooks pass in both modes. |
| **3. Roll out** | Deploy the generic instance, enable `k8s_job` processor by processor, compare the run times and failures. | No regression for a release cycle. |
| **4. Cleanup** | Remove the version-specific instances, routes and CI builds, and the Dask event based cancellation. | A single rs-dpr-service Deployment. |

Local mode (docker compose, see [Local mode](../rs-demo/docs/local-mode.md)) keeps running the driver as a
subprocess in the service container, as the `LOCAL_MODE` branch of rs-dpr-service already does.

## 9. Assumptions to verify

| Assumption | How to verify |
|---|---|
| Dask Gateway starts one thread per worker core (3 threads for `worker_cores=3`). | Dask dashboard, *Workers* page (`nthreads`), or `client.nthreads()`. |
| A cluster can be shared by several runs, from the same or different users (systematic processing). | Check the usage of `dask_cluster_instance` in the flows; the starvation risk only exists for concurrent runs. |
| `distributed.scheduler.allowed-failures` is the default (3) on the Gateway clusters. | `dask.config.get("distributed.scheduler.allowed-failures")` in a worker. |
| Memory of the EOPF-CPM subprocess is counted in the pod limit but not by the Dask worker memory manager. | Dask dashboard and `kubectl top pod` during a run. |
| Dask Gateway exposes the image of an existing cluster in its options. | `gateway.list_clusters()[i].options["image"]`, as used by [`dask_venv.py`](https://github.com/RS-PYTHON/rs-demo/blob/develop/notebooks/resources/dask_clusters/dask_venv.py). |
| The runner code works with Python 3.11 to 3.13 without extra dependencies. | It is already uploaded to the workers of the three Python versions today. |

## 10. Summary of the answers

- **Pros of the current method**: no new component, right environment for the driver, driver close to the
  scheduler, existing cancellation and log streaming, quotas enforced by the cluster.
- **Cons**: nested tasks that waste a thread per run and can deadlock a cluster, a driver that competes with the
  computation for the pod resources, a replay risk when a worker is lost, and a rs-dpr-service instance per Python
  and Dask version.
- **Better way**: run the EOPF-CPM driver in a short-lived Kubernetes Job built from the cluster image, and keep the
  Dask tasks for the computation only.
- **Infrastructure impact**: one generic rs-dpr-service instead of several, a small RBAC, driver pods with quotas
  and network policies, a possible driver node pool with pre-pulled images, and no change to the Dask clusters.

## Related pages

- [DPR processors (rs-dpr-service)](../rs-dpr-service/docs/doc/index.md)
- [Cancel a DPR run](../rs-dpr-service/docs/doc/cancel-dpr-run.md)
- [Dask](../services/virtual-environment/dask.md) and [Dask images](../rs-workflow-env/docs/dask_images.md)
- [Add and delete Dask clusters](../rs-workflow-env/docs/dask-clusters.md)
- [System architecture](architecture.md)
