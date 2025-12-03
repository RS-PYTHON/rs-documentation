#!/usr/bin/env bash
# Copyright 2025 CS Group
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

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
PROJECT_ROOT_DIR="$(realpath $SCRIPT_DIR/../..)"

# Template and output files
TEMPLATEFILE="${PROJECT_ROOT_DIR}/mkdocs.yml.tpl"
OUTPUTFILE="${PROJECT_ROOT_DIR}/mkdocs.yml"

# Execute pydoc building scripts
bash ${PROJECT_ROOT_DIR}/docs/rs-server/docs/build_pydoc.sh
bash ${PROJECT_ROOT_DIR}/docs/rs-client-libraries/docs/build_pydoc.sh
bash ${PROJECT_ROOT_DIR}/docs/rs-dpr-service/docs/build_pydoc.sh

# Locations of mkdocs.txt files
RS_SERVER_MKDOCS="${PROJECT_ROOT_DIR}/docs/rs-server/docs/mkdocs.txt"
RS_CLIENT_LIBRARIES_MKDOCS="${PROJECT_ROOT_DIR}/docs/rs-client-libraries/docs/mkdocs.txt"
RS_DPR_SERVICE_MKDOCS="${PROJECT_ROOT_DIR}/docs/rs-dpr-service/docs/mkdocs.txt"

# Template variables
RS_SERVER_PYDOC=$(<${RS_SERVER_MKDOCS})
RS_CLIENT_LIBRARIES_PYDOCS=$(<${RS_CLIENT_LIBRARIES_MKDOCS})
RS_DPR_SERVICE_PYDOCS=$(<${RS_DPR_SERVICE_MKDOCS})

# Apply template to create mkdocs.yml
echo "$(eval "echo \"$(cat $TEMPLATEFILE)\"")" > $OUTPUTFILE
