#!/usr/bin/env bash

# Clear jupyter notebook outputs (useful before commiting to git)

set -euo pipefail

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
ROOT_DIR="$(realpath $SCRIPT_DIR/..)"

for notebook in $(find $ROOT_DIR/notebooks -type f -name "*.ipynb" -not -path "*checkpoints*" | sort); do
    (
        set -x

        # Clear notebook outputs
        jupyter nbconvert --clear-output --inplace "$notebook"

        # Clear the python sub-version number
        sed -i "s|\"version\": \"3\.11\..*\"|\"version\": \"3\.11\"|g" "$notebook"
    )

done
