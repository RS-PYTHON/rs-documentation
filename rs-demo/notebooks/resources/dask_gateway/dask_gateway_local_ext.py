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

from dask_gateway_server.backends.local import LocalClusterConfig
from dask_gateway_server.traitlets import Command
from traitlets import Unicode


# Extend the upstream local cluster config with a client-supplied name.
class NamedLocalClusterConfig(LocalClusterConfig):
    # This allows the local backend to accept cluster_name in the config.
    cluster_name = Unicode(
        "",
        config=True,
        help="Logical name supplied by the client",
    )

    # Fix for a dask-gateway bug in version 2026.3.0 - TO BE REMOVED WHEN FIXED
    # In the original config (here: https://github.com/dask/dask-gateway/blob/82efdfabf723b0ff382255898a2671ebc57583be/dask-gateway-server/dask_gateway_server/backends/base.py#L244), # pylint: disable=line-too-long
    # the scheduler_cmd and worker_cmd use a deprecated command as a default value.
    # We set the correct command here until it's fixed in dask-gateway
    scheduler_cmd = Command(
        ["dask", "scheduler"],
        config=True,
        help="Shell command to start a dask scheduler.",
    )

    worker_cmd = Command(
        ["dask", "worker"],
        config=True,
        help="Shell command to start a dask worker.",
    )
