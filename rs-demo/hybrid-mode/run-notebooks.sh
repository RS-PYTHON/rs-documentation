#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
ROOT_DIR="$(realpath $SCRIPT_DIR/..)"

# Run all the demos in hybrid mode.
# This is meant to run the demos locally, but use the services deployed on the cluster.

# Configure environment
source "${SCRIPT_DIR}/resources/jupyter-env.sh"

all_errors=

# Run each demo notebook. Use a 5' timeout for each cell.
for notebook in $(find $ROOT_DIR/notebooks -type f -name "*.ipynb" -not -path "*checkpoints*" | sort); do

    _dirname="$(dirname $notebook)"
    _filename="$(basename $notebook)"

    # Run the notebook in a new shell. 
    # In case of error, save the notebook path relative to the root project.
    (set -x && cd "$_dirname" && time papermill "$_filename" /tmp/out.ipynb) || \
    all_errors="${all_errors:-}  - '$(realpath $notebook --relative-to $ROOT_DIR)'\n"
done

if [[ -n "$all_errors" ]]; then
    >&2 echo -e "\nERRORS ON NOTEBOOKS:\n${all_errors}"
    exit 1
fi