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

#######################################################################################
# Render the PlantUML diagrams of one or several RS-PYTHON repositories into SVG images.
#
# Each repository keeps the diagram sources in "docs/uml/<name>.plantuml" and the
# rendered images in "docs/images/<name>.svg". The images are committed so they can be
# displayed by GitHub and by the documentation website without any extra tool.
# The PlantUML source is also embedded inside each SVG image.
#
# Usage: render_diagrams.sh <repository_dir> [<repository_dir> ...]
# Example (from the rs-documentation directory): .github/scripts/render_diagrams.sh . ../rs-server
#
# Requirements: docker
#######################################################################################

set -euo pipefail

PLANTUML_IMAGE="${PLANTUML_IMAGE:-plantuml/plantuml:1.2025.4}"

# License header of the generated images: the license header of this script, in an XML comment
LICENSE_HEADER="<!--
$(sed -n '2,14s/^# \{0,1\}//p' "${BASH_SOURCE[0]}")
-->"

for repo in "$@"; do
    repo=$(realpath "$repo")
    uml_dir="${repo}/docs/uml"
    if [[ ! -d "$uml_dir" ]]; then
        echo "No ${uml_dir} directory, skip it."
        continue
    fi
    mkdir -p "${repo}/docs/images"

    # Render all the diagrams with the official PlantUML Docker image
    docker run --rm -u "$(id -u):$(id -g)" -e JAVA_TOOL_OPTIONS=-Duser.home=/tmp -v "${repo}/docs:/docs" -w /docs/uml "$PLANTUML_IMAGE" \
        -tsvg -charset UTF-8 -o ../images "*.plantuml"

    # Add the license header after the XML declaration (if any) of each generated image, including the
    # "<name>_001.svg", "<name>_002.svg"... images of the multi-page diagrams, and end them with a newline
    for source in "$uml_dir"/*.plantuml; do
        image="${repo}/docs/images/$(basename "${source%.plantuml}").svg"
        if [[ ! -f "$image" ]]; then
            echo "ERROR: ${image} was not generated. The @startuml name must match the file name." >&2
            exit 1
        fi
        for page in "$image" "${image%.svg}"_[0-9][0-9][0-9].svg; do
            [[ -f "$page" ]] || continue
            python3 - "$page" "$LICENSE_HEADER" <<'PYTHON'
import re
import sys

path, header = sys.argv[1], sys.argv[2]
content = open(path, encoding="utf-8").read()
if header not in content:
    match = re.match(r"\s*(<\?xml[^>]*\?>)?", content)
    prolog = match.group(1) or ""
    content = prolog + ("\n" if prolog else "") + header + "\n" + content[match.end() :].lstrip()
open(path, "w", encoding="utf-8").write(content.rstrip("\n") + "\n")
PYTHON
            echo "✓ ${page}"
        done
    done
done
