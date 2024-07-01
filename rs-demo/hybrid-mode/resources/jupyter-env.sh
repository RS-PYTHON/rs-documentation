#!/usr/bin/env bash

# Configure a local instance of jupyter for hybrid mode.
# This is meant to run the demos locally, but use the services deployed on the cluster.

if ! (return 0 2>/dev/null); then
    >&2 echo "This script must be sourced"
    exit 1
fi

# We need rs-client libraries, check that it's installed
if ! python -c "import rs_workflows" >/dev/null 2>&1; then
    >&2 echo -e "rs-client-libraries is missing (see README.md for installation instructions)"
    return 1
fi

# Idem for jupyter lab
if ! jupyter lab --version >/dev/null 2>&1; then
    >&2 echo -e "jupyterlab is missing (see README.md for installation instructions)"
    return 1
fi

# As we use the cluster, we can set local mode to false
export RSPY_LOCAL_MODE=0

# Set the URLs to use in environment variables
export RSPY_WEBSITE="https://dev-rspy.esa-copernicus.eu"

# We need an API key to authenticate to the HTTP endpoints
if [[ -z "${RSPY_APIKEY:-}" ]]; then
    >&2 echo "Generate an API key from '$RSPY_WEBSITE' then run 'export RSPY_APIKEY=your_api_key'"
    return 1
fi

# We need the S3 bucket info. Try to read them from the local .s3cfg file.
s3cfg="${HOME}/.s3cfg"
if [[ -z "${S3_ACCESSKEY:-}" || -z "${S3_SECRETKEY:-}" || -z "${S3_ENDPOINT:-}" || -z "${S3_REGION:-}" ]]; then
    if [[ -f "$s3cfg" ]]; then
        echo "Read S3 information from '$s3cfg'"        

        # Extract field value from the file
        read_s3cfg() {
            awk -F = "/$1/ "'{print $2}' "$s3cfg" | tr -d '[:space:]'
        }
        [[ -z "${S3_ACCESSKEY:-}" ]] && export S3_ACCESSKEY=$(read_s3cfg access_key)
        [[ -z "${S3_SECRETKEY:-}" ]] && export S3_SECRETKEY=$(read_s3cfg secret_key)
        [[ -z "${S3_ENDPOINT:-}" ]] && export S3_ENDPOINT=$(read_s3cfg host_bucket)
        [[ -z "${S3_REGION:-}" ]] && export S3_REGION=$(read_s3cfg bucket_location)
    fi
fi

if [[ -z "${S3_ACCESSKEY:-}" || -z "${S3_SECRETKEY:-}" || -z "${S3_ENDPOINT:-}" || -z "${S3_REGION:-}" ]]; then
    >&2 echo "Define the 'S3_ACCESSKEY', 'S3_SECRETKEY', 'S3_ENDPOINT', 'S3_REGION' env variables or use a '$s3cfg' file."
    return 1
fi

# Run docker container services (prefect and stac browser)
(set -x; cd "${SCRIPT_DIR}" && docker compose down -v; docker compose up -d)

# Shutdown the docker containers when we exit
trap "(set -x; cd "${SCRIPT_DIR}" && docker compose down -v)" EXIT

# Now prefect server and agent run locally as docker containers
export PREFECT_API_URL=http://localhost:4200/api
