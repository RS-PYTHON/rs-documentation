#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
ROOT_DIR="$(realpath $SCRIPT_DIR/..)"

# Start a local instance of jupyter lab for hybrid mode.
# This is meant to run the demos locally, but use the services deployed on the cluster.

# Configure environment
source "${SCRIPT_DIR}/resources/jupyter-env.sh"

# Run jupyter lab on the 'notebooks' directory. 
# Run Ctrl-C to exit.
jupyter lab "${ROOT_DIR}/notebooks"