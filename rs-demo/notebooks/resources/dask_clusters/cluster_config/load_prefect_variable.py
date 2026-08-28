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

"""Load Prefect variable processing-storage-configuration and extract shared-disk mounts.
This is used to configure the DPR scheduler and worker pods with the correct volumes and mounts.
The Prefect variable is expected to be a dictionary with a key "storage_configuration" that is
a list of dictionaries, each representing a storage configuration entry.
Only entries with "kind" == "shared_disk" will be included in the returned list.
"""

import asyncio
import inspect
import json
import os
from concurrent.futures import ThreadPoolExecutor

PREFECT_VAR_NAME = "processing-storage-configuration"


def get_prefect_values_from_env() -> dict:
    """
    Read the prefect payloads passed through the environment.
    This is the case when this file is imported inside a subprocess that is spawned by the
    main Jupyter environment kernel (see dask_main_env.py in function _init_dask_cluster_main_env).
    """
    raw_values = os.getenv("DPR_CONTAINER_CONFIG_PREFECT_VALUES")
    if not raw_values:
        raise RuntimeError("DPR_CONTAINER_CONFIG_PREFECT_VALUES is not set")

    try:
        parsed_values = json.loads(raw_values)
    except Exception as exc:
        raise RuntimeError(
            "DPR_CONTAINER_CONFIG_PREFECT_VALUES is not valid JSON",
        ) from exc

    if not isinstance(parsed_values, dict):
        raise RuntimeError(
            "DPR_CONTAINER_CONFIG_PREFECT_VALUES must decode to a dictionary",
        )

    return parsed_values


def load_prefect_values_from_variable() -> dict:
    """
    Load values directly from the Prefect variable service. This is the case
    when this file is ran directly in the main Jupyter environment kernel
    """
    try:
        from prefect.variables import Variable
    except ImportError as exc:
        raise RuntimeError(
            "Prefect is required to resolve DPR container config values",
        ) from exc

    try:
        result = Variable.get(PREFECT_VAR_NAME)
    except Exception as exc:
        raise RuntimeError(
            f"Unable to load Prefect variable {PREFECT_VAR_NAME!r} and no environment payload was available",
        ) from exc

    if inspect.isawaitable(result):
        try:
            asyncio.get_running_loop()
        except RuntimeError:
            result = asyncio.run(result)
        else:
            with ThreadPoolExecutor(max_workers=1) as executor:
                result = executor.submit(asyncio.run, result).result()

    if not isinstance(result, dict):
        raise RuntimeError(
            f"Prefect variable {PREFECT_VAR_NAME!r} must contain a dictionary",
        )

    return result


def get_prefect_values_sync() -> dict:
    """Load Prefect values from the environment first, then from the Prefect variable."""
    try:
        return get_prefect_values_from_env()
    except RuntimeError:
        # If the environment variable is not set, try to load from Prefect variable service
        pass

    return load_prefect_values_from_variable()


def extract_shared_disk_mounts(prefect_values: dict | None = None) -> list[dict]:
    """Extract shared-disk mounts from a storage_configuration payload."""

    values = prefect_values if prefect_values is not None else get_prefect_values_sync()
    if not isinstance(values, dict):
        raise RuntimeError("Failed to resolve Prefect values, not a dictionary")

    storage_configuration = values.get("storage_configuration")
    if not isinstance(storage_configuration, list):
        raise RuntimeError(
            "Failed to resolve Prefect values, storage_configuration is not a list",
        )

    mounts = []
    for entry in storage_configuration:
        if not isinstance(entry, dict):
            continue
        if entry.get("kind") != "shared_disk":
            continue
        if not entry.get("name") or not entry.get("absolute_path"):
            continue
        read_only = True
        opening_mode = entry.get("opening_mode")
        if opening_mode is not None and opening_mode.upper() == "CREATE_OVERWRITE":
            read_only = False

        mounts.append(
            {
                "name": str(entry["name"]),
                "mountPath": str(entry["absolute_path"]),
                "readOnly": read_only,
            },
        )

    return mounts


def resolve_volumes() -> dict:
    """Return the volumes configuration fetched from the prefect variable processing-storage-configuration"""
    prefect_values = get_prefect_values_sync()
    shared_disk_mounts = extract_shared_disk_mounts(prefect_values)

    volumes = []
    for mount in shared_disk_mounts:
        volumes.append(
            {
                "name": mount["name"],
                "persistentVolumeClaim": {"claimName": mount["name"]},
            },
        )

    return volumes
