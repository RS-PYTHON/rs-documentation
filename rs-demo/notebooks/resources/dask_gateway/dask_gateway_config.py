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

from dask_gateway_local_ext import NamedLocalClusterConfig
from dask_gateway_server.options import Options, String

# Local docker-compose runs the gateway with the local unsafe backend.
c.DaskGateway.backend_class = "dask_gateway_server.backends.local.UnsafeLocalBackend"
# Use our custom config class so the local backend accepts cluster_name.
c.LocalBackend.cluster_config_class = NamedLocalClusterConfig
# Expose cluster_name as a valid option for gateway.new_cluster(...).
c.Backend.cluster_options = Options(
    String("cluster_name", default="", label="Cluster Name"),
)
