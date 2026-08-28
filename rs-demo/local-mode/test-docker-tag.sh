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

# Run a modified local mode to test new Docker image tags

set -euo pipefail

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
ROOT_DIR="$(realpath $SCRIPT_DIR/..)"

# One single argument = the docker image tag to test
tag=${1:-}
if [[ -z "$tag" || "$tag" == "-h" || "$tag" == "--help" ]]; then
    echo "usage: '$(basename $0)' DOCKER_TAG"
    exit 1
fi

# Only alphanumeric characters, . - and _ are allowed in docker image tags.
# Replace other characters by -
tag=$(sed "s/[^a-zA-Z0-9\.\-\_]/-/g" <<< "$tag")

# Manual login to our container registry (only from a terminal)
[[ -t 1 ]] && docker login https://ghcr.io/v2/rs-python

# Go to the local-mode directory, copy the docker-compose.yml file.
cd "${ROOT_DIR}/local-mode"
dc_file="docker-compose-test-tag.yml" # note: ignored by git from .gitignore
cp "docker-compose.yml" "$dc_file"

# For each docker image hosted on our container registry, we'll try to change
# the tag :latest with the tag passed as a parameter of this script.

# Get all these docker images
all_images=$(sed -n "s|.*image:\s*\(ghcr.io/rs-python.\S*:latest\).*|\1|p" ../local-mode/docker-compose.yml)
echo -e "\nCheck for docker image tag '$tag'\n"

# echo -e "NOTE: if the below 'docker manifest inspect' commands freeze, hit ctrl-c and run the script again.\n"

# For each line
while IFS= read -r old_image ; do

    # Replace the last :<tag> by our tag
    new_image=$(sed -e "s|\(.*\):.*|\1:$tag|g" <<< "$old_image")

    (
        set +e # allow errors here

        # Check if the docker image exists in the registry
        error_message=$(docker manifest inspect "$new_image" 2>&1)
        error=$?

        # If yes, use it in the docker-compose file
        if [[ "$error" == 0 ]]; then
            echo "Use new '$new_image'"
            sed -i "s|${old_image}\s*$|$new_image|g" "$dc_file"

        # If not found, use the default tag
        elif [[ "$error_message" == "manifest unknown" ]]; then
            echo "Use default '$old_image'"

        # For any other error, exit the script
        else
            >&2 echo "$error_message"
            exit 1
        fi
    )
done <<< "$all_images"

# Pull these images
if ! docker compose -f "${dc_file}" --progress quiet pull --include-deps cicd; then
  echo
  echo "⚠️ Pull failed, retrying with verbose output:"
  echo
  docker compose -f "${dc_file}" pull --include-deps cicd
  rc=$?
  if [[ $rc -ne 0 ]]; then
    echo
    echo "❌ Pull failed again (exit code ${rc})"
    exit $rc
  fi
fi

# Show usage
echo -e "\nRun with:
cd '$(pwd)'
docker compose -f $dc_file down -v; docker compose -f $dc_file up cicd # -d for detached\n"
