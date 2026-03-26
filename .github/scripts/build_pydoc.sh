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
# This script scans each project module by module and generates a documentation
# following the same tree structure as the project, where each markdown file refers
# to a Python file. It also adds an index file with a table of content for each module,
# and a link to the index file in each markdown file of the module. A "mkdocs.txt"
# file is also generated, that contains the table of content to add in the main
# "mkdocs.yml" file used by rs-documentation.
########################################################################################

set -euo pipefail

# LOCATIONS OF IMPORTANT FOLDERS
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
PROJECT_ROOT_DIR="$(realpath $SCRIPT_DIR/../..)"


# ===== COMMON FUNCTIONS =====

create_md_file() {
    # Creates a md file in the mkdocs format for the given py file
    #
    # USAGE:
    # create_md_file PYTHON_FILE MODULE_NAME
    #
    # EXAMPLE:
    # create_md_file api/cadip_search.py rs_server_cadip

    # Retrieve input data: location of the python file (ex: subfolder/file.py), name of the python base module, and levels
    python_file=$1
    base_module=$2

    # === BUILD VARIABLES ===
    # Name of the md file: same as the source py file but with .md extension
    md_file=${base_module}"/"${python_file::-2}"md"
    # Name of the module: same as the name of the python file, but without the .py extension and replacing "/" to "." (to turn subfolders into submodules)
    pymodule=$(tr '/' '.' <<< "${base_module}.${python_file::-3}")
    # Subfolders to create: md file without the file name
    subfolder=$(dirname $md_file)
    # Location of the index file relative to the md file: replace the subfolder names with ".."
    index_location=$(realpath ${base_module}/index.md --relative-to $(dirname $md_file))

    # === CREATE AND POPULATE A MD FILE ===
    # Create subfolders and md file
    mkdir -p "$subfolder"
    # Fill the md file content
    echo "# "${md_file} > $md_file
    echo -e "\n[ << Back to index]("${index_location}")" >> $md_file
    echo -e "\n::: "${pymodule} >> $md_file
    echo -e "\n<!--- File generated automatically, do not modify it. -->" >> $md_file

    # Return name of the created md file
    echo "${python_file::-2}md"
}


create_documentation_for_module() {
    # Creates a complete documentation folder for the given python module.
    # The documentation created follows mkdocs format and has the same structure as the given module.
    # Don't forget the / at the end of the module_location.
    #
    # USAGE:
    # create_documentation_for_module MODULE_NAME MODULE_LOCATION
    #
    # EXAMPLE:
    # create_documentation_for_module "rs_server_cadip" "/home/ecombelles/workspace/rs-server/services/cadip/rs_server_cadip/"

    module_name=$1
    module_location=$2

    # === CREATE AND POPULATE INDEX FILE ===
    index_file=$module_name/index.md
    mkdir -p "$module_name"
    echo "# Python documentation for $module_name" > $index_file
    echo -e "\n## List of modules\n" >> $index_file

    # === CREATE A MD FILE FOR EACH PY FILE ===
    for file in $(find $module_location -type f -name "*.py" | grep -v "__init__"); do
        # Remove everything before the module location in the file name we are handling
        python_file=$(realpath "$file" --relative-to "$module_location")

        # Create md file
        created_file=$(create_md_file $python_file $module_name)

        # Add info for created md file in the index
        echo "Created documentation file $created_file from file $python_file."
        echo "- ["${python_file}"]("${created_file}")" >> $index_file
    done

    echo -e "\n<!--- File generated automatically, do not modify it. -->" >> $index_file
}


create_documentation_for_generic_project() {
    # Main function to generate the documentation of a generic project with all the specified modules
    #
    # USAGE:
    # create_documentation_for_generic_project PYDOC_DIR MODULES_DIR LIST_OF_MODULES

    project_pydoc_dir=$1
    project_modules_dir=$2
    local -n project_list_of_modules=$3

    # Move to pydoc dir and remove all existing content
    # (making sure we are really in a pydoc folder to avoid unfortunate consequences)
    mkdir -p "$project_pydoc_dir"
    cd $project_pydoc_dir
    case $(pwd) in *pydoc) rm -rf *;; esac

    # For each module: call create_documentation_for_module
    for i in "${!project_list_of_modules[@]}"; do
        module_name=${project_list_of_modules[i]}

        create_documentation_for_module $module_name $project_modules_dir/$module_name/

        echo "✓ Documentation for module $module_name located at $project_modules_dir/$module_name/ succesfully built."
    done
}


create_mkdocs_for_folder() {
    # Generates recursively the mkdocs table of contents of one folder in the "pydoc" folder, with correct indentation
    #
    # USAGE:
    # create_mkdocs_for_folder BASE_FOR_MKDOCS_LOCATIONS FOLDER_NAME FOLDER_LEVEL PREVIOUS_FOLDER
    # (where FOLDER_LEVEL is the the level of the given folder relatively to the first folder given
    # and BASE_FOR_MKDOCS_LOCATIONS is the path to the pydoc folder from the project root folder)
    #
    # EXAMPLE
    # create_mkdocs_for_folder rs-server/docs/doc/pydoc/ rs_server_adgs/api/ 1 rs_server_adgs/

    base_for_mkdocs_locations=$1
    folder_name=$2
    folder_level=$3
    previous_folders=$4

    # Compute indentation: 4 spaces as a base, then add two spaces for each folder level
    mkdocs_indent="    "
    for i in $(seq 1 $folder_level); do
        mkdocs_indent="${mkdocs_indent}  "
    done
    # Create line for folder name
    mkdocs="${mkdocs_indent}- ${folder_name::-1}:\n"

    cd $folder_name

    # For each file in the folder: add it as a line with a reference to the md file location
    for file in $(ls -p | grep -v /); do
        mkdocs="${mkdocs}${mkdocs_indent}  - ${file::-3}: ${base_for_mkdocs_locations}${previous_folders}${folder_name}${file}\n"
    done

    # For each folder in the folder: repeat the process to create a correct folders tree
    for folder in $(ls -p | grep / ); do
        new_level=$((folder_level + 1))
        new_mkdocs=$(create_mkdocs_for_folder $base_for_mkdocs_locations $folder $new_level "${previous_folders}${folder_name}")
        mkdocs="${mkdocs}${new_mkdocs}"
    done

    cd ..
    echo "${mkdocs}"
}


build_mkdocs_file_for_generic_project() {
    # Generates complete mkdocs file, for everything in the module names list
    #
    # USAGE:
    # build_mkdocs_file
    project_name=$1
    pydoc_dir=$2
    mkdocs_file=$3
    local -n module_names=$4

    rm -f $mkdocs_file
    cd $pydoc_dir
    base_for_mkdocs_locations="${project_name}/docs/doc/pydoc/"
    for module in "${module_names[@]}"; do
        module_mkdocs=$(create_mkdocs_for_folder $base_for_mkdocs_locations "${module}/" 0 "")
        echo -e "${module_mkdocs}" >> $mkdocs_file
    done

    echo "✓ Generated mkdocs table of contents at ${mkdocs_file}."
}


# ===== FUNCTIONS FOR RS-SERVER =====

RS_SERVER_DIR="${PROJECT_ROOT_DIR}/docs/rs-server"
RS_SERVER_PYDOC_DIR="${RS_SERVER_DIR}/docs/doc/pydoc"
RS_SERVER_MODULES_DIR="${RS_SERVER_DIR}/services"
RS_SERVER_MKDOCS_FILE="${RS_SERVER_DIR}/docs/mkdocs.txt"

# LIST OF MODULES IN RS-SERVER
# To add or remove one, make sure the lists are on the same order with the same number of elements
declare -a RS_SERVER_MODULE_LOCATIONS=(
    "${RS_SERVER_MODULES_DIR}/adgs"
    "${RS_SERVER_MODULES_DIR}/cadip"
    "${RS_SERVER_MODULES_DIR}/catalog"
    "${RS_SERVER_MODULES_DIR}/common"
    "${RS_SERVER_MODULES_DIR}/frontend"
    "${RS_SERVER_MODULES_DIR}/osam"
    "${RS_SERVER_MODULES_DIR}/prip"
    "${RS_SERVER_MODULES_DIR}/staging"
)
declare -a RS_SERVER_MODULE_NAMES=(
    "rs_server_adgs"
    "rs_server_cadip"
    "rs_server_catalog"
    "rs_server_common"
    "rs_server_frontend"
    "rs_server_osam"
    "rs_server_prip"
    "rs_server_staging"
)


create_documentation_for_rs_server() {
    # Main function to generate the documentation of rs_server with all the specified modules
    #
    # USAGE:
    # create_documentation_for_rs_server

    # Move to pydoc dir and remove all existing content
    # (making sure we are really in a pydoc folder to avoid unfortunate consequences)
    mkdir -p "$RS_SERVER_PYDOC_DIR"
    cd $RS_SERVER_PYDOC_DIR
    case $(pwd) in *pydoc) rm -rf *;; esac

    # For each module: call create_documentation_for_module
    for i in "${!RS_SERVER_MODULE_NAMES[@]}"; do
        module_name=${RS_SERVER_MODULE_NAMES[i]}
        module_location=${RS_SERVER_MODULE_LOCATIONS[i]}

        create_documentation_for_module $module_name $module_location/$module_name/

        echo "✓ Documentation for module $module_name located at $module_location succesfully built."
    done
}


# ===== CONSTANTS FOR RS-CLIENT-LIBRARIES AND RS-DPR-SERVICE =====

# For rs_client_libraries
RS_CLIENT_LIBRARIES_DIR="${PROJECT_ROOT_DIR}/docs/rs-client-libraries"
RS_CLIENT_LIBRARIES_PYDOC_DIR="${RS_CLIENT_LIBRARIES_DIR}/docs/doc/pydoc"
RS_CLIENT_LIBRARIES_MKDOCS_FILE="${RS_CLIENT_LIBRARIES_DIR}/docs/mkdocs.txt"
declare -a RS_CLIENT_LIBRARIES_MODULE_NAMES=("rs_client" "rs_common" "rs_workflows")

# For rs_dpr_service
RS_DPR_SERVICE_DIR="${PROJECT_ROOT_DIR}/docs/rs-dpr-service"
RS_DPR_SERVICE_PYDOC_DIR="${RS_DPR_SERVICE_DIR}/docs/doc/pydoc"
RS_DPR_SERVICE_MKDOCS_FILE="${RS_DPR_SERVICE_DIR}/docs/mkdocs.txt"
declare -a RS_DPR_SERVICE_MODULE_NAMES=("rs_dpr_service")


create_documentation_for_rs_server
build_mkdocs_file_for_generic_project "rs-server" $RS_SERVER_PYDOC_DIR $RS_SERVER_MKDOCS_FILE RS_SERVER_MODULE_NAMES

create_documentation_for_generic_project $RS_CLIENT_LIBRARIES_PYDOC_DIR $RS_CLIENT_LIBRARIES_DIR RS_CLIENT_LIBRARIES_MODULE_NAMES
build_mkdocs_file_for_generic_project "rs-client-libraries" $RS_CLIENT_LIBRARIES_PYDOC_DIR $RS_CLIENT_LIBRARIES_MKDOCS_FILE RS_CLIENT_LIBRARIES_MODULE_NAMES

create_documentation_for_generic_project $RS_DPR_SERVICE_PYDOC_DIR $RS_DPR_SERVICE_DIR RS_DPR_SERVICE_MODULE_NAMES
build_mkdocs_file_for_generic_project "rs-dpr-service" $RS_DPR_SERVICE_PYDOC_DIR $RS_DPR_SERVICE_MKDOCS_FILE RS_DPR_SERVICE_MODULE_NAMES
