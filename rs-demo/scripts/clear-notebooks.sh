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

# Clear jupyter notebook outputs (useful before commiting to git)

set -euo pipefail

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
ROOT_DIR="$(realpath $SCRIPT_DIR/..)"

# Remove notebook checkpoints
for checkpoint in $(find $ROOT_DIR/notebooks -type d -name ".ipynb_checkpoints"); do rm -rf "$checkpoint"; done

for notebook in $(find $ROOT_DIR/notebooks -type f -name "*.ipynb" -not -path "*checkpoints*" | sort); do
    (
        set -x

        # Clear notebook outputs
        jupyter nbconvert --clear-output --inplace "$notebook"
    )

done
