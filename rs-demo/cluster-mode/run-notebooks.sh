#!/usr/bin/env bash

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

# We need an API key to authenticate to the HTTP endpoints
if [[ -z "${RSPY_APIKEY:-}" ]]; then
    >&2 echo "Generate an API key from '$RSPY_WEBSITE' then run 'export RSPY_APIKEY=your_api_key'"
    return 1
fi

# # We need the S3 bucket info. Try to read them from the local .s3cfg file.
# s3cfg="${HOME}/.s3cfg"
# if [[ -z "${S3_ACCESSKEY:-}" || -z "${S3_SECRETKEY:-}" || -z "${S3_ENDPOINT:-}" || -z "${S3_REGION:-}" ]]; then
#     if [[ -f "$s3cfg" ]]; then
#         echo "Read S3 information from '$s3cfg'"        

#         # Extract field value from the file
#         read_s3cfg() {
#             awk -F = "/$1/ "'{print $2}' "$s3cfg" | tr -d '[:space:]'
#         }
#         [[ -z "${S3_ACCESSKEY:-}" ]] && export S3_ACCESSKEY=$(read_s3cfg access_key)
#         [[ -z "${S3_SECRETKEY:-}" ]] && export S3_SECRETKEY=$(read_s3cfg secret_key)
#         [[ -z "${S3_ENDPOINT:-}" ]] && export S3_ENDPOINT=$(read_s3cfg host_bucket)
#         [[ -z "${S3_REGION:-}" ]] && export S3_REGION=$(read_s3cfg bucket_location)
#     fi
# fi

# if [[ -z "${S3_ACCESSKEY:-}" || -z "${S3_SECRETKEY:-}" || -z "${S3_ENDPOINT:-}" || -z "${S3_REGION:-}" ]]; then
#     >&2 echo "Define the 'S3_ACCESSKEY', 'S3_SECRETKEY', 'S3_ENDPOINT', 'S3_REGION' env variables or use a '$s3cfg' file."
#     return 1
# fi

all_errors=

# For each demo notebook, sorted by name
for notebook in $(find $ROOT_DIR -type f -name "*.ipynb" -not -path "*checkpoints*" | sort); do

    _dirname="$(dirname $notebook)"
    _filename="$(basename $notebook)"

    # Run the notebook in a new shell. 
    # In case of error, save the notebook path relative to the root project.
    # NOTE: needs "pip install papermill"
    (set -x && cd "$_dirname" && time python -m papermill "$_filename" /tmp/out.ipynb) || \
    all_errors="${all_errors:-}  - '$(realpath $notebook --relative-to $ROOT_DIR)'\n"
done

if [[ -n "$all_errors" ]]; then
    >&2 echo -e "\nERRORS ON NOTEBOOKS:\n${all_errors}"
    exit 1
fi