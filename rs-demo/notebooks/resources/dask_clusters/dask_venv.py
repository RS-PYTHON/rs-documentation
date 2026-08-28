# Copyright 2023-2026 Airbus, CS Group
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Init dask clusters from Jupyter virtual environment kernels.

Main env --calls--> papermill --calls--> (in venv) notebook to init cluster --calls--> this module.
"""

import inspect
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

from dask_gateway import Gateway
from dask_gateway.client import GatewayCluster
from distributed.client import Client as DaskClient
from IPython import get_ipython
from resources.dask_clusters.dask_utils import (
    OWNER_ID,
    cluster_mode,
    get_dask_gateway,
    local_mode,
)

##########################
# Global implementations #
##########################


def printflush(message: str):
    """Print and flush immediately so the calling notebook sees the progress."""
    print(message)
    sys.stdout.flush()


def dpr_label(image: str, base_label: str) -> str:
    """Format label for DPR dask clusters as base_label.OWNER_ID.DOCKER_VERSION e.g. 'dask-l0.userA.latest'"""

    # Add the owner id to the label
    final_label = f"{base_label}.{OWNER_ID}"

    # Add the docker image version (after the ':', if any) to the label
    if len(splits := image.split(":")) > 1:
        final_label += f".{splits[-1]}"

    if len(final_label) > 63:
        final_label = final_label[:63].rstrip("-_.")

    return final_label


def read_jupyter_token():
    """Read the JUPYTERHUB_API_TOKEN environment variable from the Prefect blocks."""
    # It is used only in cluster mode. In local mode we set an empty value.
    if local_mode:
        os.environ["JUPYTERHUB_API_TOKEN"] = ""
        return

    # Call the local module/app in command line
    app = str((Path(__file__).parent / "read_jupyter_token.py").resolve())
    print(f"Call: {app!r}")

    try:
        result = subprocess.run(  # nosec B603
            app,
            check=True,
            capture_output=True,
            text=True,
        )
        os.environ["JUPYTERHUB_API_TOKEN"] = str(result.stdout).strip()
    except subprocess.CalledProcessError as e:
        print(e.stderr, file=sys.stderr)
        raise


def _init_dask_cluster_venv(
    scale: int,
    image: str,
    python_packages: list[str],
    cluster_label: str,
    worker_cores: int,
    worker_memory: float,
    scheduler_memory_limit: int,
    worker_extra_pod_config: dict,
    scheduler_extra_pod_config: dict,
    worker_extra_container_config: dict,
    scheduler_extra_container_config: dict,
    local_mode_address: str,
    gateway_namespace=os.getenv("DASK_GATEWAY_NAMESPACE", "dask-gateway"),
    **kwargs,
) -> tuple[Gateway, GatewayCluster, DaskClient]:
    """
    Read existing or create new dask cluster from Jupyter virtual environment kernels.

    Args:
        scale: number of dask workers to create
        image: docker image name to use for the workers. Only needed in cluster mode.
        python_packages: show the version of these python packages in the logs
        cluster_label: custom label to identify the cluster e.g. "dask-proc"
        worker_cores: number of CPU per worker
        worker_memory: memory per worker in GB
        scheduler_memory_limit: memory for scheduler in GB
        worker_extra_pod_config: any extra configuration for the worker pods
        scheduler_extra_pod_config: any extra configuration for the scheduler pods
        worker_extra_container_config: any extra configuration for the worker container
        scheduler_extra_container_config: any extra configuration for the scheduler container
        local_mode_address: name of the env var that contains the dask gateway url in local mode
        gateway_namespace: dask gateway namespace
        kwargs: additional keywoard arguments to pass to the method "gateway.new_cluster"

    NOTE: to find the maximum cluster resources that you can request per node, first init a dask cluster, then in k9s
    go to your allocated dask-worker -> push 'o' (Show Node) -> push 'd' (Describe) -> check 'Allocatable' values.
    Then decrease a little bit these values because the nodes also run other services.

    Several workers can fit into a single node depending on the resources you requested for each worker. Else new nodes
    will be allocated. To find the maximum of nodes you can request, in k9s, type
    ':nodepools' -> find your nodeAffinity -> check the 'MAX' column value.

    For worker_extra_pod_config=dpr_worker_pod_config and nodeAffinity=dask_worker_on_demand
    we have max: 3 CPU, 12GB RAM, 8 nodes.

    For worker_extra_pod_config=dpr_scheduler_pod_config and nodeAffinity=dask_scheduler
    we have max: 7 CPU, 58GB RAM, 1 node.
    """
    # Print args passed to this function
    sig, loc = inspect.signature(_init_dask_cluster_venv), locals()
    args = {param.name: loc[param.name] for param in sig.parameters.values()}
    printflush(json.dumps(args, indent=2))

    # Read the JUPYTERHUB_API_TOKEN env var from the Prefect blocks
    read_jupyter_token()

    gateway_address = os.environ[
        "DASK_GATEWAY_ADDRESS" if cluster_mode else local_mode_address
    ]
    printflush(
        f"Connecting to dask gateway for {cluster_label!r}: {gateway_address} ...",
    )
    gateway = get_dask_gateway(gateway_address)

    if cluster_mode:
        gateway_public = os.environ["DASK_GATEWAY_PUBLIC"]
    else:
        # In local mode, the gateway address configured in .env) is like http://dask-<proc>:8000
        # The corresponding public address (configured in nginx.conf) is: http://localhost/dask/<proc>
        pattern = re.compile(r"dask-([^:]+):\d+")
        gateway_public = pattern.sub(r"localhost/dask/\1", gateway_address)

    # Sort the clusters by newest first
    clusters = sorted(
        gateway.list_clusters(),
        key=lambda cluster: cluster.start_time,
        reverse=True,
    )
    for cluster in clusters:
        printflush(f"image = {cluster.name}")

    # Get existing dask cluster name, if any.
    existing = None
    if clusters:

        # In local mode, get the existing cluster with the expected cluster name.
        if local_mode:
            existing = next(
                (
                    report.name
                    for report in clusters
                    if isinstance(report.options, dict)
                    and report.options.get("cluster_name") == cluster_label
                ),
                None,
            )

        # In cluster mode, also check the docker image name and cluster name
        else:
            existing = next(
                (
                    report.name
                    for report in clusters
                    if (report.options.get("image") == image)
                    and (report.options.get("cluster_name") == cluster_label)
                ),
                None,
            )

    # If a cluster has already been initialized, retrieve it
    if existing:
        printflush(f"Get existing dask cluster: {existing!r}")
        cluster = gateway.connect(existing)

    # Else create one
    else:
        if local_mode:
            printflush("Create new dask cluster")
            options = {"cluster_name": cluster_label} | kwargs

        else:  # cluster_mode
            printflush(f"Create new dask cluster from docker image: {image!r}")
            options = {
                "worker_cores": worker_cores,
                "worker_memory": worker_memory,
                "cluster_max_workers": scale + 1,
                "cluster_max_cores": (scale + 1) * worker_cores,
                "cluster_max_memory": (scale + 1)
                * worker_memory
                * (2**30),  # from GB to B
                "scheduler_memory_limit": scheduler_memory_limit,
                "namespace": gateway_namespace,
                "image": image,
                "cluster_name": cluster_label,
                "scheduler_extra_pod_labels": {"cluster_name": cluster_label},
                "worker_extra_pod_config": worker_extra_pod_config,
                "scheduler_extra_pod_config": scheduler_extra_pod_config,
                "worker_extra_container_config": worker_extra_container_config,
                "scheduler_extra_container_config": scheduler_extra_container_config,
            } | kwargs

        valid_options = list(gateway.cluster_options())
        discard = [o for o in options if o not in valid_options]
        if discard:
            printflush(f"Discard invalid gateway options: {json.dumps(discard)}")
        options = {key: value for key, value in options.items() if key in valid_options}
        cluster = gateway.new_cluster(**options)

    printflush(
        f"Dask dashboard for {cluster_label!r}: {cluster.dashboard_link.replace(gateway_address, gateway_public)}",
    )

    # Scale the cluster and get the client
    gateway.scale_cluster(cluster.name, scale)
    client = cluster.get_client()

    # Wait for all workers to be up
    tries = 0
    while True:
        scaled = len(client.scheduler_info()["workers"])
        printflush(f"Dask workers for {cluster_label!r} are up: {scaled}/{scale}")
        if scaled >= scale:
            break
        tries += 1
        if tries >= float("inf"):  # deactivate timeout
            raise TimeoutError(
                f"Error waiting for all Dask workers for {cluster_label!r} to be up: {scaled}/{scale}",
            )
        time.sleep(5)

    # Save ClusterInfo value as a IPython variable, so it is shared with other notebooks,
    # even from different kernels.
    cluster_info = {
        "jupyter_token": os.environ["JUPYTERHUB_API_TOKEN"],
        "dask_gateway_address": gateway_address,
        "cluster_label": cluster_label,
        "cluster_instance": cluster.name,
    }
    share_values = {"cluster_info": cluster_info}

    obfuscated_info = cluster_info | {
        "jupyter_token": f"{cluster_info['jupyter_token'][:8]}***",
    }
    printflush(json.dumps(obfuscated_info, indent=2))

    def pip_freeze(pkg_names: list[str]) -> list[str]:
        """Run a pip freeze from inside a dask pod"""
        from pip._internal.operations import freeze

        return [
            pkg
            for pkg in freeze.freeze()
            if any(
                [
                    pkg.startswith(f"{name}==") or pkg.startswith(f"{name} @")
                    for name in pkg_names
                ],
            )
        ]

    pip_freeze_result = client.submit(pip_freeze, python_packages).result()
    printflush(
        f"Python package versions (pip freeze):\n{json.dumps(pip_freeze_result, indent=2)}",
    )

    # Save other vars to be read from main env
    if local_mode:
        share_values.update(
            {
                "gateway_address": gateway_address,
                "gateway_public": gateway_public,
            },
        )

    # Save it under a key = id of the parent of the current process = the papermill subprocess,
    # when run from the main env.
    get_ipython().db[str(os.getppid())] = share_values

    return gateway, cluster, client


###############################
# Init each dask cluster type #
###############################


def init_dask_cluster_cpm2_venv(
    image: str = "",
    cluster_label: str = "",
    **kwargs,
):
    """Read existing or create new dask cluster."""
    return _init_dask_cluster_venv(
        image=image,
        python_packages=["eopf"],
        cluster_label=cluster_label or dpr_label(image, "dask-cpm2"),
        local_mode_address="DASK_GATEWAY_CPM2_ADDRESS",
        **kwargs,
    )


def init_dask_cluster_cpm3_venv(
    image: str = "",
    cluster_label: str = "",
    **kwargs,
):
    """Read existing or create new dask cluster."""
    return _init_dask_cluster_venv(
        image=image,
        python_packages=["eopf"],
        cluster_label=cluster_label or dpr_label(image, "dask-cpm3"),
        local_mode_address="DASK_GATEWAY_CPM3_ADDRESS",
        **kwargs,
    )


def init_dask_cluster_l0_venv(
    image: str = "",
    cluster_label: str = "",
    **kwargs,
):
    """Read existing or create new dask cluster."""
    return _init_dask_cluster_venv(
        image=image,
        python_packages=["eopf", "l0"],
        cluster_label=cluster_label or dpr_label(image, "dask-l0"),
        local_mode_address="DASK_GATEWAY_L0_ADDRESS",
        **kwargs,
    )


def init_dask_cluster_mockup_venv(
    image: str = "",
    cluster_label: str = "",
    **kwargs,
):
    """Read existing or create new dask cluster."""
    return _init_dask_cluster_venv(
        image=image,
        python_packages=["eopf"],
        cluster_label=cluster_label or dpr_label(image, "dask-eopf-mockup"),
        local_mode_address="DASK_GATEWAY_EOPF_MOCKUP_ADDRESS",
        **kwargs,
    )


def init_dask_cluster_s1ard_venv(
    image: str = "",
    cluster_label: str = "",
    **kwargs,
):
    """Read existing or create new dask cluster."""
    return _init_dask_cluster_venv(
        image=image,
        python_packages=["eopf", "s1-ard"],
        cluster_label=cluster_label or dpr_label(image, "dask-s1ard"),
        local_mode_address="DASK_GATEWAY_S1ARD_ADDRESS",
        **kwargs,
    )


def init_dask_cluster_s3olci_venv(
    image: str = "",
    cluster_label: str = "",
    **kwargs,
):
    """Read existing or create new dask cluster."""
    return _init_dask_cluster_venv(
        image=image,
        python_packages=["eopf", "s3olci"],
        cluster_label=cluster_label or dpr_label(image, "dask-s3olci"),
        local_mode_address="DASK_GATEWAY_S3OLCI_ADDRESS",
        **kwargs,
    )


def init_dask_cluster_staging_venv(
    image: str = "",
    cluster_label: str = "",
    **kwargs,
):
    """Read existing or create new dask cluster."""
    return _init_dask_cluster_venv(
        image=image,
        python_packages=["rs-server-common", "rs-server-staging"],
        cluster_label=cluster_label or os.environ["RSPY_DASK_STAGING_CLUSTER_NAME"],
        local_mode_address="DASK_GATEWAY_STAGING_ADDRESS",
        **kwargs,
    )
