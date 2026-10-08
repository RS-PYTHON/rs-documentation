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

set -euo pipefail

# Read RSPY environment variables
source /docker/compose/dir/.env

# Give all permissions to the docker named volumes "rspy_working_dir".
# This is for the docker containers that will be run as non-root.
(set -x; chmod 777 ${RSPY_WORKING_DIR})

# Remove the filelock files (even if they should not cause trouble anyway)
(set -x; rm -f ${RSPY_WORKING_DIR}/rs_server_common.db.database.lock)

# The .env file defines the config file paths as they should be installed
# inside the Docker container.
# for target_config in ${EODAG_ADGS_CONFIG} ${EODAG_CADIP_CONFIG}; do

#     # The source config file is in ./config with the same filename
#     source_config=/docker/compose/dir/config/$(basename ${target_config})

#     # Create target directory and copy file
#     mkdir -p $(dirname ${target_config})
#     (set -x; cp -f ${source_config} ${target_config})

# done
