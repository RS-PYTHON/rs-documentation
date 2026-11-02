# Running a DPR processor on a Dask cluster: architecture review

This page explains how a DPR processor is run on a [Dask](https://www.dask.org/) cluster, analyses the strengths and
weaknesses of the current design, and proposes a better one, with its impact on the infrastructure. It is written
for the developers and the infrastructure operators of RS-Python, and the first sections are meant for beginners.

> **Status**
>
> Sections 1 to 4 describe the system **as implemented today**, checked against the source code of
> [rs-dpr-service](https://github.com/RS-PYTHON/rs-dpr-service),
> [rs-demo](https://github.com/RS-PYTHON/rs-demo) and [EOPF-CPM](https://cpm.pages.eopf.copernicus.eu/eopf-cpm/main/index.html).
> Sections 5 to 9 are an **architecture proposal**, not yet implemented. The points that could not be verified from
> the code are listed in [Assumptions to verify](#10-assumptions-to-verify).
>
> A key constraint drives the whole analysis: the pod of rs-dpr-service is small (see
> [The resource constraint](#the-resource-constraint-where-can-the-eopf-cpm-driver-run)), so the EOPF-CPM driver
> **cannot** run there. Any proposal must give the driver enough RAM and CPU.

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
| **The driver gets enough RAM and CPU** | This is the main reason for the design. The pod of rs-dpr-service is small (request 256 Mi and 100m CPU, limit 1000 Mi and 500m CPU in the [rs-helm chart](https://github.com/RS-PYTHON/rs-helm/blob/develop/charts/rs-dpr-service/values.yaml)). Running `eopf trigger` inside a worker pod gives it access to the resources of a worker (up to 3 CPU and 12 GB RAM on the `dask_worker_on_demand` pool). The resources are *available*, not *reserved*: see the matching con below. |
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
| **The driver resources are shared, not reserved** | The EOPF-CPM subprocess (graph construction, in-process orchestration, S3 transfers, logging) takes RAM and CPU from the worker pod that also runs the tasks. Nothing guarantees it a minimum, and Dask's memory manager does not see the subprocess memory. An out-of-memory kill of the pod kills the driver and the computation together. This is the other side of the first pro. | High |
| **A worker failure can replay the whole run** | Dask reschedules the tasks of a lost worker (`distributed.scheduler.allowed-failures`, 3 by default). Task #1 is the whole processor run, so it may be started again with its side effects (outputs written twice). | Medium |
| **Version coupling** | rs-dpr-service must match the Python and Dask versions of each processor, hence one Deployment, Helm values, route and CI build per version. Adding a processor with a new Python or Dask version means deploying a new instance. | High |
| **Secrets travel through Dask** | The JupyterHub API token and the S3 credentials are put in the serialized task, so they pass through the scheduler. | Medium |
| **Harder to observe and debug** | A failure can be in the REST service, in task #1, in the subprocess or in task #2. Task #1 shows as a long task in the Dask dashboard that is not real work. | Low |
| **Opaque lifecycle** | A run is a Python task, not a Kubernetes object: no `kubectl get jobs`, no TTL, no native deadline. | Low |

![Thread starvation](../images/dask-processing-thread-starvation.svg)

**Conclusion.** The idea is not wrong: running the driver next to the scheduler, from the cluster image, with
more RAM and CPU than the service pod, is sound and it is a real requirement. The weakness is *how* the driver
gets its resources. Putting it in a Dask task makes it consume, without any reservation, the resources of the
workers it is supposed to orchestrate, and keeps rs-dpr-service tied to the Dask version. The nested task is what
turns a performance inefficiency into a risk of deadlock.

### The resource constraint: where can the EOPF-CPM driver run?

The driver is the process that runs `eopf trigger`: it loads the payload, builds the workflow, connects to the
Dask cluster as a client, submits the tasks, follows their progress and finalises the products (`EORunner.run` in
[EOPF-CPM](https://cpm.pages.eopf.copernicus.eu/eopf-cpm/main/index.html)). Its RAM and
CPU needs depend on the processor and on the size of the products, and we do not have measurements yet (see
[Measure the driver footprint](#measure-the-driver-footprint)). What is known:

- the service pod is far too small for it: limit of 1000 Mi and 500m CPU, shared with the REST API and with all the
  runs of this instance;
- several runs can be in progress at the same time, each with its own driver;
- the EOPF-CPM release notes already mention memory issues in the staging and S3 upload code (e.g. "High memory
  usage when uploading staged products to S3", #1251).

![Driver placement](../images/dask-processing-driver-placement.svg)

| Placement | RAM and CPU for the driver | Isolated from the computation | Removes nested tasks | Removes version coupling | Verdict |
|---|---|---|---|---|---|
| **A. In the rs-dpr-service pod** | Too small today. Raising the limits means bigger always-on pods, multiplied by the number of instances (one per Python/Dask version), sized for the worst case of concurrent runs. | No: shared with the API and the other drivers | Yes | No | Rejected |
| **B. In a Dask worker** (today) | Up to the worker size (3 CPU, 12 GB), but not reserved | No | No | No | Works, fragile |
| **C. In a Kubernetes Job** | Requested and limited for the driver alone, set per processor | Yes | Yes | Yes | **Recommended** |
| **D. In a Job on the scheduler node pool** | Large node (up to 7 CPU, 58 GB), mostly used by the scheduler memory request | Yes (own pod) | Yes | Yes | Fallback, a single node |

Scaling rs-dpr-service horizontally does not fix placement A: a run is long, its state and logs live in the
instance that started it, so the load cannot be rebalanced, and a pod sized for the largest driver is idle most of
the time.

### Measure the driver footprint

Before fixing the size of the driver, measure it, for the heaviest processors and for several concurrent runs:

| What | How |
|---|---|
| Peak RAM and CPU of the driver | Run the proof of concept with a Job without limits and read `kubectl top pod` and the Prometheus metrics `container_memory_working_set_bytes` and `container_cpu_usage_seconds_total` of the driver pod (Grafana, [rs-infra-monitoring](https://github.com/RS-PYTHON/rs-infra-monitoring)). |
| Same figure in the current design | Compare the memory of the worker *pod* (cgroup metrics) with the memory reported by Dask for the worker process in the dashboard: the difference is the driver subprocess (and the other processes of the pod). |
| Memory timeline of the computation | EOPF-CPM has a Dask memory sampler and a performance report, enabled by the Dask context settings of the payload (see the `DaskContext` class). |
| Effect of the products size | Repeat with the smallest and the biggest products of each processor. |

Keep the maximum measured, add a margin (e.g. 25 %), and use it as the request and limit of the driver.

## 5. Options

| Option | Description | Removes nested tasks | Removes version coupling | Enough RAM/CPU for the driver | Infrastructure change | Effort |
|---|---|---|---|---|---|---|
| **A. Keep as is** | Reference. | No | No | Yes, but not reserved | None | None |
| **B. Mitigate in place** | Keep the design. Call [`secede()`](https://distributed.dask.org/en/stable/task-launch.html) at the start of task #1 so it releases its thread while it waits, and/or start the workers with more threads than cores, and/or use one cluster per run. | Partly (no more deadlock, still two levels) | No | Same as A | None | Small |
| **B2. Reserve the driver in Dask** | Keep the design, but tag task #1 with a [Dask worker resource](https://distributed.dask.org/en/stable/resources.html) (e.g. `DRIVER=1`) and size the workers so that a driver always has its share: at most one driver per worker, and a worker size that includes the driver. Combined with `secede()`. | Partly | No | Better: bounded number of drivers per worker, but still no memory reservation | Cluster options (worker `--resources`), to be verified with Dask Gateway | Small to medium |
| **C. Driver in rs-dpr-service** | rs-dpr-service runs `eopf trigger` itself (subprocess in its own pod); EOPF-CPM connects to the cluster. No task #1. | Yes | No (EOPF-CPM must be installed in each instance, with the right versions) | **No**: pod of 1000 Mi / 500m CPU, to be multiplied and kept always on | Much bigger pods | Medium |
| **D. One Kubernetes Job per run (recommended)** | rs-dpr-service creates a short-lived Kubernetes Job from the **cluster image**, with its own requests and limits. The Job runs `eopf trigger`, which connects to the existing cluster. | Yes | **Yes**: a single generic rs-dpr-service | **Yes, reserved and sized per processor** | New RBAC, driver pods, quotas, node pool | Medium |
| **E. Prefect-native** | The Prefect flow itself starts the Kubernetes Job (Prefect Kubernetes work pool), and rs-dpr-service disappears or only keeps the catalogue of processors. | Yes | Yes | Yes (work pool job template) | Prefect work pool | Large (changes the public API) |

**Why not C.** It removes the nested task, but the service pod has 1000 Mi and 500m CPU, far less than a driver
may need. Making it big enough means big always-on pods, one set per Python/Dask version, that must absorb the
drivers of all the concurrent runs, without isolation between the runs of different users, and with no way to
spread the load. It also keeps EOPF-CPM, Python and Dask in each rs-dpr-service image: the version coupling
remains. This option is only suitable for the local mode (debugging).

**Why B2 is not enough.** Dask resources only limit how many tasks run at the same time on a worker; they do not
reserve memory or CPU. The driver subprocess is outside Dask's accounting. B2 is a cheap improvement to deploy
while D is being built.

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
| 5 | rs-dpr-service creates a Kubernetes `Job` (one pod, `restartPolicy: Never`, `backoffLimit: 0`) with that image and with **its own `requests` and `limits` for RAM and CPU**, sized for the driver of this processor (see [Sizing and placing the driver pod](#sizing-and-placing-the-driver-pod)). The payload location, the S3 settings and the OpenTelemetry trace context are passed as environment variables, the JupyterHub token in a per-run `Secret` owned by the Job. |
| 6 | The driver pod downloads the configuration and runs `eopf_otel trigger local payload.yaml`: it is the code of `ProcessorCaller.init`/`trigger` of today, packaged as a small runner that works with Python 3.11 to 3.13. |
| 7 | EOPF-CPM connects to the existing cluster (`reuse_cluster`) and submits its tasks. These are the **only** Dask tasks. |
| Logs and status | rs-dpr-service reads the pod logs and the Job status with the Kubernetes API (the logs are also collected by Alloy and Loki), and exposes them as today to the Prefect flow. |
| Cancellation | rs-dpr-service deletes the Job. The pod receives a SIGTERM, which EOPF-CPM already handles; the termination grace period replaces the `time.sleep(60)` followed by SIGKILL. |

### What is gained

- **No nested tasks**: all the threads of the workers compute. No thread starvation and no deadlock.
- **The driver is isolated and has the RAM and CPU it needs**: its memory and CPU are *requested* (so reserved by
  the Kubernetes scheduler) and *limited* in its own pod. The small rs-dpr-service pod is not involved, the driver
  does not compete with the computation, and its crash does not kill a worker.
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
- **A sizing responsibility**: the driver size is now an explicit setting, and a wrong value shows up as an
  `OOMKilled` driver (too small) or as unused reserved capacity (too big).

### Sizing and placing the driver pod

The fact that the service pod is small is the reason why the driver moves to a Job, so the size of the Job is the
critical parameter of this design.

| Topic | Proposal |
|---|---|
| **Where the size is defined** | A `driver_resources` setting (`cpu`, `memory`) with a default value in the Helm values of rs-dpr-service, overridable per processor, next to the existing `resources_min` of the [task table](../rs-client-libraries/docs/doc/flows/tasktable-payload.md) (which today describes the Dask workers). The processor owner knows best. |
| **Request and limit** | Equal (Kubernetes QoS class *Guaranteed*): the memory is reserved, the pod is not evicted before the others, and the CPU is not throttled by neighbours. |
| **Initial values** | To be measured (see [Measure the driver footprint](#measure-the-driver-footprint)). Until then, start from the measured peak plus a margin, and keep a generous default for the biggest processors. |
| **Concurrent runs** | A `ResourceQuota` on the namespace of the Jobs caps the total RAM and CPU of the drivers. Beyond it, the Job stays `Pending`: rs-dpr-service reports the run as *queued* and applies a start timeout (`activeDeadlineSeconds` does not cover the pending phase, so the service watches it). |
| **Under-sizing** | If the driver pod ends with `OOMKilled`, rs-dpr-service reports a clear error ("driver out of memory, limit = X") instead of a generic failure, so that the size can be corrected. |
| **Placement** | A small dedicated **driver node pool** (preferred), or the scheduler node pool as a fallback (see the sizing note in [Impact on the infrastructure](#7-impact-on-the-infrastructure)). Not the worker pool, to keep the drivers from taking capacity from the computation. |
| **Per-user fairness** | One Job per run, labelled with the user and the cluster, so the quotas and the dashboards can be split by user. |

If the Kubernetes API cannot be used (e.g. a restricted environment), a degraded alternative is option B2 with a
dedicated driver capacity in the Dask cluster: it bounds the number of drivers per worker, but it does not reserve
memory.

## 7. Impact on the infrastructure

![Infrastructure impact](../images/dask-processing-infrastructure-impact.svg)

| Area | Today | Proposed | Action |
|---|---|---|---|
| **rs-dpr-service Deployments** | One per Python/Dask version (3 today) | One generic Deployment (replicas for availability, not for versions) | Merge the `rs-dpr-service-py-*` applications of [rs-server-deployment](https://github.com/RS-PYTHON/rs-server-deployment), keep the old ones during the migration. |
| **Routing (Envoy Gateway)** | One route per processor to the right instance | A single route | Simplify the routes and the Helm values. |
| **CI/CD and images** | One rs-dpr-service image per Python/Dask version | One image, plus the runner packaged in the Dask images | Update the [publish workflow](ci-cd.md) and the [Dask images](../rs-workflow-env/docs/dask_images.md) build. |
| **RBAC** | None | `ServiceAccount` and `Role` in the namespace of the Jobs: `create`, `get`, `list`, `watch`, `delete` on `jobs`; `create` on `secrets` (no `get` or `list`); `get`, `list` on `pods` and `pods/log`. | Add to the [rs-helm](https://github.com/RS-PYTHON/rs-helm) chart. Restrict to the namespace and to the Jobs labelled by the service. |
| **Node pools** | Drivers run in the `dask_worker_on_demand` pool, inside the workers | Driver pods need a place to run, with a reserved RAM and CPU | A small dedicated driver pool, see the sizing note below. |
| **Quotas** | Cluster options limit the workers; the driver is not accounted | The driver pods are bounded and accounted | `ResourceQuota` and `LimitRange` on the namespace in which the Jobs run; `requests` equal to `limits` set on each Job from the `driver_resources` setting. |
| **rs-dpr-service pod** | Small (256 Mi / 100m request, 1000 Mi / 500m limit) | **Unchanged: it can stay small**, as it no longer runs a driver or a Dask client with the processor environment | Keep the current Helm resources; optionally reduce them. |
| **Network policies** | rs-dpr-service reaches Dask Gateway | The driver pod also reaches Dask Gateway (and the scheduler through it), S3 and the OpenTelemetry endpoint | Add the egress rules for the driver pods label. |
| **Secrets** | The JupyterHub token travels in the Dask task | One short-lived `Secret` per run, owned by the Job (deleted with it) | Mount the secret as an environment variable of the driver pod. |
| **Observability** | Logs of the service and of the workers | Logs of the driver pod, Job metrics | Add the Job dashboards in [rs-infra-monitoring](https://github.com/RS-PYTHON/rs-infra-monitoring); keep the trace context propagation (`TRACEPARENT`) which already works with a subprocess. |
| **Dask clusters** | `scale` workers, one of which is partly used by the drivers | The same cluster, with all threads available to the computation | Optionally reduce the size of the clusters, which are no longer penalised by the drivers. |
| **Cost** | Constant | A few short-lived small pods, fewer always-on service pods | Neutral to slightly positive. |

**Sizing note.** The init notebooks report that a worker node offers at most 3 CPU and 12 GB RAM, and that the
scheduler node offers at most 7 CPU and 58 GB RAM, most of it requested by the scheduler by default
(`scheduler_memory_limit`). The driver size is to be measured (see
[Measure the driver footprint](#measure-the-driver-footprint)); it must fit in a node of the pool where it runs,
and the image of the cluster, which is large, should already be on the node. Two possibilities:

1. Add a small **driver node pool** (a few nodes, scale to zero or to one) sized from the measured driver size
   times the number of concurrent runs, and pre-pull the Dask images with a DaemonSet or an image cache, to keep
   the start-up delay low.
2. Schedule the drivers on the scheduler node pool, which already has the image, provided the scheduler memory
   request is reduced to leave room. There is a single node, so the drivers of all the runs share it.

Option 1 is preferred because it isolates the drivers from the scheduler and scales with the number of runs.

## 8. Impact on the local mode

The [local mode](../rs-demo/docs/local-mode.md) runs the whole system with a docker compose file
([rs-demo/local-mode](https://github.com/RS-PYTHON/rs-demo/tree/develop/local-mode)), for the development and for the
CI, which runs the demo notebooks on it. It has no Kubernetes, so **a Kubernetes Job cannot be used there**. The
local mode must keep working, and ideally keep testing the same code as the cluster mode.

### How it works today

| Aspect | Cluster mode | Local mode (docker compose) |
|---|---|---|
| Dask Gateway | One central gateway, JupyterHub authentication | One gateway **per `dask-*` container** (`UnsafeLocalBackend`), basic authentication (`LOCAL_DASK_USERNAME`) |
| Scheduler and workers | Pods, with their own CPU and RAM | Processes inside the `dask-*` container (`DASK_MEMORY_EOPF`, `DASK_CORES_EOPF` of the `.env` file) |
| Cluster image | In the cluster options (`options["image"]`) | Not available: the local backend only knows the `cluster_name` option |
| rs-dpr-service | One Deployment per Python/Dask version | One container per version (the demos only use the one of the mockup processor) |
| Driver (task #1) | In a worker pod | In a worker process of the `dask-*` container |
| Debug | Not possible | Experimental `local_cluster` setting: EOPF-CPM runs in the service container with its own `LocalCluster`. It needs an image variant of rs-dpr-service that contains EOPF-CPM. |

Note that the `LOCAL_MODE` branch of rs-dpr-service that runs EOPF-CPM in the service container (`trigger`) is only
used by the debug setting, not by the nominal local mode.

### Principle: one runner, several launchers

The cluster-mode design is split in two parts, so that only the second one depends on the platform:

1. **The runner**: the code that downloads the configuration, runs `eopf trigger`, streams the logs and returns an
   exit code. It is the same in all the modes, and it is installed in the images of the Dask clusters (both the
   Kubernetes images and the `local` images, built by [rs-workflow-env](https://github.com/RS-PYTHON/rs-workflow-env)).
2. **The launcher**: the component of rs-dpr-service that starts the runner with the requested resources, follows
   its logs and status, and stops it. It is selected by a setting, for example `RSPY_DRIVER_MODE`.

![Launchers](../images/dask-processing-local-mode.svg)

| Mode | Launcher | Where the driver runs |
|---|---|---|
| Cluster | `KubernetesJobLauncher` | A Kubernetes Job (see [Recommended design](#6-recommended-design-a-driver-job-per-run)) |
| Local (nominal) | `DockerLauncher` | A short-lived container started from the image of the `dask-*` container |
| Debug | `SubprocessLauncher` | A subprocess, or the process itself, in the service container |

In code terms, the launcher is a small interface (`start`, `logs`, `status`, `cancel`, `cleanup`), so the rest of
rs-dpr-service (job table, log forwarding, cancellation endpoint) no longer knows how the driver is started. It
also allows unit tests with a fake launcher.

### Options for the local launcher

| Option | Description | Pros | Cons | Verdict |
|---|---|---|---|---|
| **L1. Docker API (recommended)** | rs-dpr-service starts one container per run with the Docker API, using the Python Docker SDK. Requests are limited with `mem_limit` and `nano_cpus`, the container joins `rspy-network`, and it is removed at the end. | Same semantics as a Job: one isolated driver per run, resource limits, `OOMKilled` detection, stop with a grace period (SIGTERM then SIGKILL), labels for the cleanup. Tests the launcher code path in the CI demos. | Needs access to the Docker socket. | **Recommended** |
| **L2. Runner sidecar** | A small HTTP service started in each `dask-*` container (or next to it) that starts and stops the runner processes. | No Docker socket. Works with Podman and Windows without changes. | A new service to write and maintain (start, logs, status, cancel): it re-implements a job controller. Limits apply to the sidecar, not to each run. | If the Docker socket is forbidden |
| **L3. In the `dask-*` container** | `docker exec` of the runner in the existing `dask-*` container. | No new image. | Needs the Docker socket as well, and the driver shares the container with the scheduler and the workers: the problem of the current design remains. | Rejected |
| **L4. In the service container** | The runner runs as a subprocess of rs-dpr-service. | No privilege. | EOPF-CPM and the processors must be installed in the service image, which is what the generic service avoids, and the driver is again in the small service container. | Debug only |

### What changes, for option L1

| Where | Change |
|---|---|
| **rs-dpr-service** | Add the launcher interface and the three launchers. Keep a single service image for the local mode as in cluster mode. Map the `driver_resources` setting to Docker limits. Remove the driver containers left over by a crashed service at start-up (containers with a `rs-python.run-id` label). |
| **Cluster image in local mode** | The local Dask Gateway does not give the image of a cluster. Read it from a setting, a map from the cluster label to the image, e.g. `RSPY_DRIVER_IMAGES='{"dask-cpm3": "ghcr.io/rs-python/dask/cpm3/local:latest"}'`, defined in the `.env` file of the demo. The compose files that test the temporary image tags (`docker-compose-test-tag.yml`) must set the same map with the tested tag. |
| **docker-compose.yml** | Give the service access to the Docker API through a restricted proxy (a [docker-socket-proxy](https://github.com/Tecnativa/docker-socket-proxy) container that only allows the container endpoints) instead of mounting `/var/run/docker.sock` directly. Merge the `rs-dpr-service_py<python>-<dask>` services into one, and update the upstream of `nginx.conf` accordingly. |
| **Environment of the driver** | The driver container receives the same variables as the service: S3 settings, OpenTelemetry, `LOCAL_DASK_USERNAME` and `LOCAL_DASK_PASSWORD`, and the gateway address (`DASK_GATEWAY_<CLUSTER>_ADDRESS`, resolved on `rspy-network`). Nothing new: they are already copied to the worker today (`copy_caller_env`). |
| **Resources** | On a laptop, the defaults must be small. `DASK_MEMORY_EOPF` is 32G today for the local workers: the `driver_resources` defaults for the local mode should be set in the `.env` file, with the heavy processors documented as "need a big machine". |
| **rs-workflow-env** | Install the runner in the `local` images of the Dask clusters, like in the Kubernetes images, so that both start the same code. |
| **Debug** | Keep the `local_cluster` setting and the `localcluster` image variants of rs-dpr-service, which contain EOPF-CPM. The `SubprocessLauncher` replaces today's `LOCAL_MODE` branch. |
| **Documentation** | Update [Local mode](../rs-demo/docs/local-mode.md) (services table, environment variables, debug section). |

### Points of attention

- **Security**: access to the Docker socket is equivalent to root access on the host. Use the socket proxy, enable it
  only in the local mode, and never in the cluster mode, where the Kubernetes RBAC applies. This is acceptable for a
  developer machine or a CI runner, not for a shared server.
- **Network**: the driver container must reach the gateway of the `dask-*` container, S3 and the OpenTelemetry
  endpoint: it must join `rspy-network` (a fixed name, defined in the compose files).
- **Fidelity**: the local mode does not test the Kubernetes specifics (RBAC, quotas, scheduling of the Job). They are
  covered by the "Test deployment" workflows, which deploy on a test Kubernetes cluster
  (see [Repositories and CI/CD](ci-cd.md#workflows)).
- **Migration**: the local mode can be migrated first, as a way to validate the runner and the launcher interface
  with the CI demos, before any change in the Kubernetes deployment.

## 9. Migration plan

| Phase | Content | Exit criterion |
|---|---|---|
| **0. Measure and secure** | Measure the driver RAM and CPU in the current design (worker pod memory minus Dask worker memory), check the number of threads per worker, reproduce the starvation with *N* concurrent runs on a small cluster, apply options B and B2 (`secede()`, driver resource, or one run per cluster) as a safety net. | The driver footprint is known, the deadlock is reproduced and then no longer occurs. |
| **1. Proof of concept** | Package the runner, create the Job by hand with the `cpm3` image, first without limits then with the measured size, run an existing payload. Measure the driver memory and start-up delay. | A full run succeeds with the driver outside the cluster; `driver_resources` values are known. |
| **2. Service integration** | Introduce the runner and the launcher interface in rs-dpr-service, with a setting `RSPY_DRIVER_MODE` (`dask_task` for the current behaviour, `docker`, `k8s_job`, `subprocess`). Start with the `docker` launcher in the local mode, then implement the `k8s_job` launcher: Job creation, logs, status, cancellation, cleanup, RBAC. Keep the current mode as default. | The existing tests and the [rs-demo](https://github.com/RS-PYTHON/rs-demo) notebooks pass in the local mode with `docker` and in the cluster mode with `k8s_job`. |
| **3. Roll out** | Deploy the generic instance, enable `k8s_job` processor by processor, compare the run times and failures. | No regression for a release cycle. |
| **4. Cleanup** | Remove the version-specific instances, routes and CI builds, the `dask_task` mode and the Dask event based cancellation. | A single rs-dpr-service Deployment, a single service in the local compose file. |

## 10. Assumptions to verify

| Assumption | How to verify |
|---|---|
| Dask Gateway starts one thread per worker core (3 threads for `worker_cores=3`). | Dask dashboard, *Workers* page (`nthreads`), or `client.nthreads()`. |
| A cluster can be shared by several runs, from the same or different users (systematic processing). | Check the usage of `dask_cluster_instance` in the flows; the starvation risk only exists for concurrent runs. |
| `distributed.scheduler.allowed-failures` is the default (3) on the Gateway clusters. | `dask.config.get("distributed.scheduler.allowed-failures")` in a worker. |
| Memory of the EOPF-CPM subprocess is counted in the pod limit but not by the Dask worker memory manager. | Dask dashboard and `kubectl top pod` during a run. |
| The RAM and CPU needs of the driver (the EOPF-CPM process that runs `eopf trigger`) are well above the limits of the rs-dpr-service pod (1000 Mi, 500m CPU). | [Measure the driver footprint](#measure-the-driver-footprint), on the heaviest processors. This is what the design depends on. |
| The driver RAM needs depend on the product size and the processor, not only on the processor. | Same measurements with the smallest and biggest products; if confirmed, `driver_resources` may need to be overridable per run. |
| Worker resources (`--resources`) can be set through the Dask Gateway cluster options (needed by option B2 only). | Check the cluster options (`gateway.cluster_options()`) and the Dask Gateway configuration in [rs-workflow-env](https://github.com/RS-PYTHON/rs-workflow-env). |
| A driver container on `rspy-network` can reach the local Dask Gateway and the scheduler of a `dask-*` container with the basic authentication (the scheduler address returned by the local gateway must be reachable from outside the container). | Start a container on the network and run the `eopf trigger` of the mockup processor with `reuse_cluster`; rs-dpr-service already does the equivalent from its own container. |
| The Docker socket can be exposed (through a proxy) to the service in the developer machines and in the CI runners. | Check the CI workflows and the platforms supported for the local mode (Linux, macOS, Windows, Podman). Fall back to the runner sidecar (L2) otherwise. |
| The `local` images of the Dask clusters can embed the runner like the Kubernetes images. | Check the build of the images in [rs-workflow-env](https://github.com/RS-PYTHON/rs-workflow-env). |
| Dask Gateway exposes the image of an existing cluster in its options. | `gateway.list_clusters()[i].options["image"]`, as used by [`dask_venv.py`](https://github.com/RS-PYTHON/rs-demo/blob/develop/notebooks/resources/dask_clusters/dask_venv.py). |
| The runner code works with Python 3.11 to 3.13 without extra dependencies. | It is already uploaded to the workers of the three Python versions today. |

## 11. Summary of the answers

- **Pros of the current method**: the EOPF-CPM driver gets far more RAM and CPU than the small rs-dpr-service pod
  could give it (the main reason for the design), no new component, right environment for the driver, driver close
  to the scheduler, existing cancellation and log streaming, quotas enforced by the cluster.
- **Cons**: nested tasks that waste a thread per run and can deadlock a cluster, a driver whose resources are
  shared with the computation and not reserved, a replay risk when a worker is lost, and a rs-dpr-service instance
  per Python and Dask version.
- **Better way**: run the EOPF-CPM driver in a short-lived Kubernetes Job built from the cluster image, with its own
  reserved and per-processor RAM and CPU, and keep the Dask tasks for the computation only. Running the driver in
  the rs-dpr-service pod is rejected, as it is too small. A cheaper stopgap is `secede()` plus Dask worker resources
  (options B and B2).
- **Infrastructure impact**: one generic rs-dpr-service instead of several, which can stay small, a small RBAC,
  driver pods with reserved resources, quotas and network policies, a dedicated driver node pool with pre-pulled
  images (or the scheduler node pool as a fallback), and no change to the Dask clusters.
- **Local mode**: a Job does not exist in docker compose, so the driver start becomes a launcher selected by a
  setting. Same runner everywhere; a Docker launcher (through a restricted socket proxy) in the local mode, which
  also exercises the launcher code in the CI demos; a subprocess launcher kept for debugging.

## Related pages

- [DPR processors (rs-dpr-service)](../rs-dpr-service/docs/doc/index.md)
- [Cancel a DPR run](../rs-dpr-service/docs/doc/cancel-dpr-run.md)
- [Dask](../services/virtual-environment/dask.md) and [Dask images](../rs-workflow-env/docs/dask_images.md)
- [Add and delete Dask clusters](../rs-workflow-env/docs/dask-clusters.md)
- [System architecture](architecture.md)
