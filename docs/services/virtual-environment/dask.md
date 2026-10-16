# Dask

[Dask](https://www.dask.org/) is the Python library used by RS-Python for parallel computing. The Dask clusters
are created on the Kubernetes cluster by [Dask Gateway](https://gateway.dask.org/). They run:

- the [staging](../../rs-server/docs/doc/users/staging.md) tasks, that copy the products from the stations into the
  object storage,
- the [DPR processors](../../rs-dpr-service/docs/doc/index.md).

Each Dask cluster is made of a *scheduler* and of one or several *workers*, created from a Docker image that
contains the code to run (e.g. a DPR processor). The images are described in
[Dask images](../../rs-workflow-env/docs/dask_images.md).

## Cluster labels

The flows and services find the Dask cluster to use thanks to its **label**, e.g. `dask-staging` for the staging
cluster, or the `dask_cluster_label` parameter of the [processing flows](../../rs-client-libraries/docs/doc/flows/index.md).
The available clusters are started by the administrators or by the users themselves, see
[Add and delete Dask clusters](../../rs-workflow-env/docs/dask-clusters.md). To list the running clusters from a
notebook:

```python
from dask_gateway import Gateway

gateway = Gateway()  # the address and authentication are configured in JupyterHub
for cluster in gateway.list_clusters():
    print(cluster.name, cluster.status, cluster.options)
```

## Dask dashboard

The [Dask dashboard](https://docs.dask.org/en/latest/dashboard.html) shows the progress of the computations at a
lower level than Prefect: tasks in progress, memory and CPU used by each worker, task stream, logs... The link to
the dashboard of the cluster used by a DPR processor run is written in the logs of the processing flow, e.g.
`https://dash-dask.processing.ops.rs-python.eu/clusters/dask-gateway.<cluster-id>/status`. See the
[Dask dashboard documentation](https://docs.dask.org/en/latest/dashboard.html) for the description of its pages.

!!! warning "Resources"

    The workers of a Dask cluster have a fixed amount of CPU and RAM. If a processor needs more memory than
    available, the workers are killed and restarted by Dask, and the processing fails. Choose the cluster size
    according to the needs of the processor (see the `resources_min` section of the processor
    [task table](../../rs-client-libraries/docs/doc/flows/tasktable-payload.md)).

More information is available in the [Dask documentation](https://docs.dask.org/) and in the
[Dask Gateway documentation](https://gateway.dask.org/).
