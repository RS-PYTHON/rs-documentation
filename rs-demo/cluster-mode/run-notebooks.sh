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
#set -x

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
# ROOT_DIR="$(realpath $SCRIPT_DIR/..)"
ROOT_DIR=$SCRIPT_DIR

# Run all the demos in cluster mode.
# This is meant to run the demos locally from a JupyterHub terminal, by using the services deployed on the cluster.

# This file contains your saved API key
if [[ -f ~/.env ]]; then source ~/.env; fi

# We need rs-client libraries, check that it's installed
if ! python -c "import rs_client" >/dev/null 2>&1; then
    >&2 echo -e "rs-client-libraries is missing (see README.md for installation instructions)"
    return 1
fi

# As we use the cluster, we can set local mode to false
export RSPY_LOCAL_MODE=0

all_ok=
all_errors=

# For each demo notebook, sorted by name
for notebook in $(find $ROOT_DIR -type f -name "*.ipynb" -not -path "*checkpoints*" | sort); do

    _dirname="$(dirname $notebook)"
    _filename="$(basename $notebook)"
    _relative="$(realpath $notebook --relative-to $ROOT_DIR)"

    # Run the notebook in a new shell.
    # In case of error, save the notebook path relative to the root project.
    # NOTE: needs "pip install papermill"
    (set -x && cd "$_dirname" && time python -m papermill "$_filename" /tmp/out.ipynb) && \
    all_ok="${all_ok:-}  - '$_relative'\n" || \
    all_errors="${all_errors:-}  - '$_relative'\n"
done

if [[ -n "$all_ok" ]]; then
    >&2 echo -e "\nNOTEBOOKS RUN SUCCESSFULLY:\n${all_ok}"
fi

if [[ -n "$all_errors" ]]; then
    >&2 echo -e "\nERRORS ON NOTEBOOKS:\n${all_errors}"
    exit 1
fi
