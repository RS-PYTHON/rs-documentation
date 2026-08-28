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

"""Init dask clusters from the main Jupyter environment kernel."""

import asyncio
import json
import os
import subprocess
from pathlib import Path

from IPython import get_ipython
from IPython.display import Markdown, display
from resources import utils
from resources.dask_clusters import dask_utils
from resources.dask_clusters.dask_utils import local_mode
from rs_client.ogcapi.dpr_client import ClusterInfo

try:
    from prefect.variables import Variable as PrefectVariable
except ImportError:
    PrefectVariable = None

NOTEBOOK_DIR = Path(__file__) / "../../../init-dask-clusters"

##########################
# Global implementations #
##########################


async def _init_dask_cluster_main_env(
    name: str,
    notebook_path: Path,
    kwargs: dict = {},
) -> ClusterInfo:
    """
    From the main Jupyter environment kernel, we call a notebook (in command line) that will
    read an existing or create a new dask cluster.

    Args:
        name: Dask cluster user-friendly identifier
        notebook_path: Notebook to read
        kwargs: parameters to pass to the notebook (https://papermill.readthedocs.io/en/latest/usage-parameterize.html)
    """
    notebook_path = notebook_path.resolve()

    # Use papermill to call the notebook in a subprocess.
    # It will use the venv kernel that is defined in the notebook.
    params = [e for key, value in kwargs.items() for e in ["-p", key, str(value)]]
    cmd = [
        "papermill",
        str(notebook_path),
        f"{Path.home()}/.papermill.ipynb",
        "--log-output",
        *params,
    ]

    # Display markdown link to the notebook
    relative_from_home = str(notebook_path.relative_to(Path.home(), walk_up=True))
    relative_from_current = str(notebook_path.relative_to(Path.cwd(), walk_up=True))
    display(
        Markdown(f"### Run notebook: [{relative_from_home}]({relative_from_current})"),
    )

    if PrefectVariable is not None:
        try:
            print(
                "Fetching values from processing-storage-configuration prefect variable...",
            )
            prefect_values = await PrefectVariable.get(
                "processing-storage-configuration",
            )
        except Exception as exc:
            raise RuntimeError(
                "Could not get the prefect processing-storage-configuration "
                "variable. Exception",
            ) from exc

        if isinstance(prefect_values, dict):
            os.environ["DPR_CONTAINER_CONFIG_PREFECT_VALUES"] = json.dumps(
                prefect_values,
            )

    print(f"[{name}] Command line: {' '.join(cmd)!r}")
    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )

    # Read papermill output line by line
    keep_open = False
    while proc.stdout:
        line = (await proc.stdout.readline()).decode("utf-8")
        if not line:  # process has finished
            break

        # Print line if not empty
        if line := line.rstrip():
            print(f"[{name}] {line}")

        # The notebook will hit this line after it has finished initializing the dask cluster
        if dask_utils.KEEP_THIS_NOTEBOOK_OPEN in line:
            keep_open = True
            break

    # Test subprocess status code when it ends (if we don't keep it alive)
    if (not keep_open) and (status_code := await proc.wait()):
        print(f"[{name}] === AN ERROR OCCURRED ===")
        raise RuntimeError(
            f"Dask cluster initialization failed with status: {status_code}",
        )

    # NOTE: we don't want to kill the subprocess, we need to keep it alive.
    # It will be killed when you restart your Jupyter kernel.

    # Read ClusterInfo value as a IPython variable
    share_values = get_ipython().db.pop(str(proc.pid))
    _cluster_info = share_values["cluster_info"]
    cluster_info = ClusterInfo(**_cluster_info)

    # Set environment for payload (=job order) files.
    # Don't do it for the staging.
    if "staging" not in str(notebook_path):

        # In local mode, the dask gateway address is different for each eopf cluster (l0, l1, ...)
        # NOTE: not sure this is used in fact. Maybe this info is already calculated by rs-dpr-service.
        # To be confirmed.
        if local_mode:
            os.environ["DASK_GATEWAY_ADDRESS"] = share_values["gateway_address"]
            os.environ["DASK_GATEWAY_PUBLIC"] = share_values["gateway_public"]

            # Refresh Prefect blocks to pass these env vars to the dask workers
            # NOTE: this is not thread-safe, these variables will be overridden if we init
            # several clusters from the same demo.
            utils.init_prefect_blocks(_sync=True)

    return cluster_info


###############################
# Init each dask cluster type #
###############################


async def init_dask_cluster_cpm2(**kwargs):
    """Read existing or create new dask cluster."""
    return await _init_dask_cluster_main_env(
        "cpm2",
        NOTEBOOK_DIR / "init_dask_cluster_cpm2.ipynb",
        kwargs,
    )


async def init_dask_cluster_cpm3(**kwargs):
    """Read existing or create new dask cluster."""
    return await _init_dask_cluster_main_env(
        "cpm3",
        NOTEBOOK_DIR / "init_dask_cluster_cpm3.ipynb",
        kwargs,
    )


async def init_dask_cluster_mockup(**kwargs):
    """Read existing or create new dask cluster."""
    return await _init_dask_cluster_main_env(
        "mockup",
        NOTEBOOK_DIR / "init_dask_cluster_mockup.ipynb",
        kwargs,
    )


async def init_dask_cluster_l0(**kwargs):
    """Read existing or create new dask cluster."""
    return await _init_dask_cluster_main_env(
        "l0",
        NOTEBOOK_DIR / "init_dask_cluster_l0.ipynb",
        kwargs,
    )


async def init_dask_cluster_s1ard(**kwargs):
    """Read existing or create new dask cluster."""
    return await _init_dask_cluster_main_env(
        "s1ard",
        NOTEBOOK_DIR / "init_dask_cluster_s1ard.ipynb",
        kwargs,
    )


async def init_dask_cluster_s3olci(**kwargs):
    """Read existing or create new dask cluster."""
    return await _init_dask_cluster_main_env(
        "s3olci",
        NOTEBOOK_DIR / "init_dask_cluster_s3olci.ipynb",
        kwargs,
    )


async def init_dask_cluster_staging(**kwargs):
    """Read existing or create new dask cluster."""
    return await _init_dask_cluster_main_env(
        "staging",
        NOTEBOOK_DIR / "init_dask_cluster_staging.ipynb",
        kwargs,
    )
