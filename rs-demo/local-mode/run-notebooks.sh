#!/usr/bin/env bash

# Run all the notebooks using docker containers

set -euo pipefail

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
ROOT_DIR="$(realpath $SCRIPT_DIR/..)"

#
# Find the docker image:tag to use

docker_image="ghcr.io/rs-python/rs-client-libraries_jupyter"

# Docker tag to use = 1st parameter passed to the script, or latest by default.
docker_tag=${1:-latest}

set +e # allow errors here

# Check if the docker image exists in the registry
error_message=$(set -x; docker manifest inspect "${docker_image}:${docker_tag}" 2>&1)
error=$?

# If yes, use it to run the notebooks
if [[ "$error" == 0 ]]; then
    docker_image_tag="${docker_image}:${docker_tag}"

# If not found, use the default tag
elif [[ "$error_message" == "manifest unknown" ]]; then
    docker_image_tag="${docker_image}:latest"

# For any other error, exit the script
else
    >&2 echo "$error_message"
    exit 1
fi

set -e # restore checking errors
echo "docker_image_tag=$docker_image_tag"

#
# Run services

# Call the health endpoint until it returns a status code OK
wait_for_service() {

    port="$1"
    health="$2"
    
    local i=0
    while [[ ! $(set -x; curl "localhost:$port/$health" 2>/dev/null) ]]; do
        sleep 2
        i=$((i+1)); ((i>=10)) && >&2 echo "Error reaching 'localhost:$port/$health'" && exit 1
    done
    return 0
}
# Same ports as in docker-compose.yml
wait_for_service 8001 "health" # adgs
wait_for_service 8002 "health" # cadip
wait_for_service 8003 "_mgmt/ping" # catalog

# Run the notebook from a container, in the same network than the docker-compose,
# with the same options than the jupyter service in the docker-compose.
# Read the environment variables before running the notebook.
(
    set -x; 
    docker run --rm \
        --network rspy-network \
        -v $ROOT_DIR:$ROOT_DIR \
        -v rspy-demo_rspy_working_dir:/rspy/working/dir \
        "${docker_image_tag}" \
        "${SCRIPT_DIR}/scripts/run-notebooks-from-container.sh"
)
