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

"""Utility module for dask, called from the main and virtual Jupyter environment kernels."""

import os
import socket

import ipywidgets as widgets
from dask_gateway import Gateway
from dask_gateway.auth import BasicAuth, JupyterHubAuth
from dask_gateway.client import GatewayCluster
from distributed.client import Client as DaskClient

# Use this str in notebooks to tell that the notebook must be kept open (alive) when called from
# command line so the cluster local variables are not garbage collected and the cluster stays up in local mode.
KEEP_THIS_NOTEBOOK_OPEN = "Keep this notebook open (when called from command line)"

# In local mode, all your services are running locally.
# In cluster mode, we use the services deployed on the RS-Server website.
# This configuration is set in an environment variable.
local_mode: bool = os.getenv("RSPY_LOCAL_MODE") == "1"
cluster_mode: bool = not local_mode

OWNER_ID = (
    os.environ["JUPYTERHUB_USER"] if cluster_mode else os.environ["RSPY_HOST_USER"]
)


def get_ip_address() -> str:
    """Return IP address, see: https://stackoverflow.com/a/166520"""
    return socket.gethostbyname(socket.gethostname())


def get_dask_gateway(
    address: str,
) -> Gateway:
    """Return dask gateway"""

    if cluster_mode:
        try:
            # NOTE: this should be the common token read from the Prefect block
            token = os.environ["JUPYTERHUB_API_TOKEN"]
            print(f"JUPYTERHUB_API_TOKEN: '{token[:8]}***'")
            auth = JupyterHubAuth(token)
        except KeyError as error:
            raise KeyError(
                "JUPYTERHUB_API_TOKEN environment variable is missing",
            ) from error

    else:  # local mode
        auth = BasicAuth(
            os.environ["LOCAL_DASK_USERNAME"],
            os.environ["LOCAL_DASK_PASSWORD"],
        )

    return Gateway(address=address, auth=auth)


def get_existing_cluster(
    address: str,
    name: str,
) -> tuple[Gateway, GatewayCluster, DaskClient]:
    """
    Return existing dask cluster from its gateway address and cluster name.
    Raise exceptions if the gateway or cluster do not already exist.
    Note: this is run from prefect worker so the print or logging won't show.
    """
    try:
        gateway = get_dask_gateway(address)
        cluster = gateway.connect(name)
        client = cluster.get_client()
        return gateway, cluster, client

    except Exception as exception:
        raise ConnectionError(
            f"Error connecting to dask gateway: {address!r} and cluster name: {name!r}",
        ) from exception


# Checkbox asking the user if they want to shutdown the clusters
# (used to avoid shutting down the clusters by mistake)
shutdown_checkbox = widgets.Checkbox(
    value=False,
    description="Shutdown the dask clusters",
    indent=False,
)


def shutdown_dask_clusters(gateway: Gateway, name: str | None):
    """
    Shutdown the given gateway cluster, or all clusters if the name is None.
    """
    for cluster in gateway.list_clusters():
        try:
            if (name is None) or (name == cluster.name):
                cluster = gateway.connect(cluster.name)
                cluster.shutdown()
                print(f"Shutting down cluster {cluster.name!r} ...")
        except Exception as e:
            print(f"Error shutting down cluster {cluster.name!r}: {e}")


def close_dask_clusters(gateway, cluster, client):
    """Close dask gateway, cluster and client python objects."""

    # First client, then cluster, then gateway
    for obj in (client, cluster, gateway):
        if obj:
            obj.close()
