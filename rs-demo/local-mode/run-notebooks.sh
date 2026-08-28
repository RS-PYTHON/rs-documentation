#!/usr/bin/env bash

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

# Run all the notebooks using docker containers

set -euo pipefail

# Call the health endpoint until it returns a status code OK
wait_for_service() {

    port="$1"
    health="$2"

    local i=0
    while [[ ! $(set -x; curl "localhost:$port/$health" 2>/dev/null) ]]; do
        sleep 2
        i=$((i+1)); ((i>=20)) && >&2 echo "Error reaching 'localhost:$port/$health'" && exit 1
    done
    return 0
}
# Same ports as in docker-compose.yml
wait_for_service 8001 "health" # adgs
wait_for_service 8002 "health" # cadip
wait_for_service 8003 "catalog/_mgmt/health" # catalog
wait_for_service 8888 "login" # jupyter

# Run the notebooks from the jupyter service from the docker-compose.
set -x;
docker exec --user=root jupyter /scripts/run-notebooks-from-container.sh
