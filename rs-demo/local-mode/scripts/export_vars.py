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

"""
This script converts a YAML configuration describing external data sources
into a `.env` file containing environment variables.

It is run by build-env-external-data-sources job from rs-demo/.github/workflows/run_demos.yml
"""

import sys

import yaml

# Prefix used for all generated environment variable keys
PREFIX = "RSPY__TOKEN__"


def to_env_key(*parts):
    """
    Build a standardized environment variable key.

    Each part is uppercased and joined using double underscores,
    and prefixed with a constant PREFIX.

    Example:
        to_env_key("service", "station1", "authentication", "username")
        -> "RSPY__TOKEN__SERVICE__STATION1__AUTHENTICATION__USERNAME"

    Args:
        *parts (str): Components of the environment variable name.

    Returns:
        str: Formatted environment variable key.
    """
    return PREFIX + "__".join(part.upper() for part in parts)


def write_env_file(env_vars, path="local-mode/.env-external-data-sources"):
    """
    Write environment variables to .env-external-data-sources in local-mode/ .

    Args:
        env_vars (dict): Dictionary of environment variables (key -> value).
        path (str): Output file path.
    """
    with open(path, "w", encoding="utf-8") as f:
        for key, value in env_vars.items():
            if value:
                f.write(f"{key}={value}\n")


def main():
    """
    Main entry point for the script.

    This function:
    1. Validates CLI arguments.
    2. Loads a YAML configuration file.
    3. Extracts external data source definitions.
    4. Converts them into environment variables.
    5. Writes them to .env-external-data-sources.

    Expected YAML structure:
        external_data_sources:
            domain:
                service:
                    name: <service_name>
                    ...
                authentication:
                    <key>: <value>
                trusteddomains: [list]

    Usage:
        python generate_env_from_yaml.py <yaml_file>
    """
    if len(sys.argv) != 2:
        print("Usage: generate_env_from_yaml.py <yaml_file>", file=sys.stderr)
        sys.exit(1)

    with open(sys.argv[1], encoding="utf-8") as f:
        config = yaml.safe_load(f)

    data_sources = config.get("external_data_sources", {})
    env_vars = {}

    for station_key, station_data in data_sources.items():

        station = station_key.upper()

        service_name = station_data.get("service", {}).get("name")
        if not service_name:
            print(f"Missing service.name for {station_key}", file=sys.stderr)
            continue

        service = service_name.upper()

        for key, value in station_data.get("service", {}).items():
            env_key = to_env_key(service, station, "SERVICE", key)
            env_vars[env_key] = value

        for key, value in station_data.get("authentication", {}).items():
            parts = key.split("_")
            env_key = to_env_key(service, station, "AUTHENTICATION", *parts)
            if value == "${access_key}":
                value = "${S3_ACCESSKEY}"
            if value == "${secret_key}":
                value = "${S3_SECRETKEY}"
            env_vars[env_key] = value

        if "domain" in station_data:
            env_key = to_env_key(service, station, "DOMAIN")
            env_vars[env_key] = station_data["domain"]

        trusted = station_data.get("trusteddomains", [])
        if trusted:
            value = "[" + ", ".join(trusted) + "]"
            env_key = to_env_key(service, station, "TRUSTEDDOMAINS")
            env_vars[env_key] = value

    write_env_file(env_vars)


if __name__ == "__main__":
    main()
