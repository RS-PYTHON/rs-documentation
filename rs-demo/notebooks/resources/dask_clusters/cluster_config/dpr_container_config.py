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

"""Extra configuration for the DPR scheduler and worker containers."""

from .load_prefect_variable import extract_shared_disk_mounts, get_prefect_values_sync


def resolve_dpr_container_config() -> dict:
    """Return the DPR container config with shared-disk mounts from Prefect."""
    prefect_values = get_prefect_values_sync()
    shared_disk_mounts = extract_shared_disk_mounts(prefect_values)

    return {"volumeMounts": shared_disk_mounts}


dpr_container_config = resolve_dpr_container_config()
print(f"[dpr_container_config] Resolved configuration: {dpr_container_config}")
