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

"""Utility Python module for the tutorials.

WARNING: AFTER EACH MODIFICATION, RESTART THE JUPYTER NOTEBOOK KERNEL !
"""

import csv
import difflib
import json
import logging
import os
import time
from datetime import datetime

import boto3
import requests
from pystac import (
    Collection,
    Extent,
    Item,
    ItemCollection,
    SpatialExtent,
    TemporalExtent,
)
from pystac_client import CollectionClient
from pystac_client.item_search import DatetimeLike
from rs_client.ogcapi.dpr_client import DprClient
from rs_client.ogcapi.staging_client import StagingClient
from rs_client.osam_client import OsamClient
from rs_client.rs_client import RsClient
from rs_client.stac.auxip_client import AuxipClient
from rs_client.stac.cadip_client import CadipClient
from rs_client.stac.catalog_client import CatalogClient
from rs_common.logging import Logging
from rs_common.prefect_utils import init_prefect_blocks, save_bucket_credentials

# Variables
# Set logger level to info
Logging.level = logging.INFO
logger = Logging.default(__name__)

# In local mode, all your services are running locally.
# In cluster mode, we use the services deployed on the RS-Server website.
# This configuration is set in an environment variable.
local_mode: bool = os.getenv("RSPY_LOCAL_MODE") == "1"
cluster_mode: bool = not local_mode

# Is this code run from the ci/cd or manually ? By default: manually.
from_cicd: bool = os.getenv("RSPY_FROM_CICD") == "1"

# In cluster mode, you need an API key to access the RS-Server services.
apikey: str | None = None

# Client instances
auxip_client: AuxipClient = None
cadip_client: CadipClient = None
catalog_client: CatalogClient = None
staging_client: StagingClient = None
dpr_client: DprClient = None
osam_client: OsamClient = None

# HTTP request session
http_session: requests.Session = requests.Session()

# We use these bucket names that are deployed on the cluster.
# RS-Server has read/write access to these buckets, but as an end-user, you won't manipulate them directly.
# Except in local mode, where we use a local SeaweedFS object storage instance.
# We need to manually create the buckets.
RSPY_TEMP_BUCKET = os.environ["RSPY_TEMP_BUCKET"]

# For local mode only
if local_mode:
    BUCKET_CONFIG_FILE_PATH = os.environ["BUCKET_CONFIG_FILE_PATH"]
    RSPY_HOST_USER = os.environ["RSPY_HOST_USER"]  # username

OWNER_ID = os.environ["JUPYTERHUB_USER"] if cluster_mode else RSPY_HOST_USER

# STAC catalog sample collection name
TEST_COLLECTION: str = "my_test_collection"

# Define a search interval
start_date = datetime(2000, 1, 1)
stop_date = datetime(2024, 1, 1)

#
# Functions


def pretty_print(any_dict: dict, indent=2):
    """Pretty print any dict e.g. JSON data."""
    print(json.dumps(any_dict, indent=indent))


def sort_dict_or_list(obj: dict | list) -> dict | list:
    """Sort a nested dict or list, recursively"""
    if isinstance(obj, dict):
        return {key: sort_dict_or_list(value) for key, value in sorted(obj.items())}
    if isinstance(obj, list):
        return [sort_dict_or_list(item) for item in obj]
    return obj


def compare_dict(old_values: dict, new_values: dict) -> str:
    """Compare two dicts, return differences as a unified diff string (or empty string if none)"""
    if old_values == new_values:
        return ""
    return "".join(
        difflib.unified_diff(
            json.dumps(sort_dict_or_list(old_values), indent=2).splitlines(
                keepends=True,
            ),
            json.dumps(sort_dict_or_list(new_values), indent=2).splitlines(
                keepends=True,
            ),
            fromfile="old_values",
            tofile="new_values",
        ),
    )


def get_buckets_from_config_file() -> list:
    """Returns a list of the buckets names in the configuration file."""
    data = []
    # This function is not called in cluster mode but this is an extra check just in case
    if not local_mode:
        return data
    with open(BUCKET_CONFIG_FILE_PATH, newline="", encoding="utf-8") as csvfile:
        reader = csv.reader(csvfile, skipinitialspace=True)
        for line in reader:
            data.append(line)
    return [row[4] for row in data]


def get_s3_client():
    """
    Return a boto3 s3 client from the
    S3_ACCESSKEY, S3_SECRETKEY, S3_ENDPOINT, S3_REGION environment variables.
    """
    s3_session = boto3.session.Session()
    return s3_session.client(
        service_name="s3",
        aws_access_key_id=os.environ["S3_ACCESSKEY"],
        aws_secret_access_key=os.environ["S3_SECRETKEY"],
        endpoint_url=os.environ["S3_ENDPOINT"],
        region_name=os.environ["S3_REGION"],
    )


def create_s3_buckets():
    """In local mode only: create the s3 buckets, if they do not already exists."""
    if not local_mode:
        return
    s3_client = get_s3_client()
    rspy_catalog_buckets = get_buckets_from_config_file()
    rspy_catalog_buckets.append(RSPY_TEMP_BUCKET)
    for bucket in rspy_catalog_buckets:
        try:
            logger.debug(f"Creating bucket {bucket}")
            s3_client.create_bucket(Bucket=bucket)
        except (
            s3_client.exceptions.BucketAlreadyExists,
            s3_client.exceptions.BucketAlreadyOwnedByYou,
        ):
            pass  # do nothing if already exists


def init_rsclient(owner_id=None):
    """Init RsClient instances"""
    global auxip_client, cadip_client, catalog_client, staging_client, dpr_client, prip_client, osam_client

    # In local mode, the service URLs are hardcoded in the docker-compose file
    if local_mode:
        rs_server_href = None  # not used
    # In cluster mode, they are set in an environment variables
    else:
        rs_server_href = os.environ["RSPY_WEBSITE"]
    # Init a generic RS-Client instance. Pass the:
    #   - RS-Server website URL
    #   - API key
    #   - ID of the owner of the STAC catalog collections.
    #     By default, this is the user login from the keycloak account, associated to the API key.
    #     Or, in local mode, this is the local system username.
    #     Else, your API Key must give you the rights to read/write on this catalog owner (see next cell).
    #   - Logger (optional, a default one can be used)
    generic_client = RsClient(
        rs_server_href,
        rs_server_api_key=apikey,
        owner_id=owner_id,
        logger=None,
    )

    # From this generic instance, get child instances
    auxip_client = generic_client.get_auxip_client()
    prip_client = generic_client.get_prip_client()
    cadip_client = generic_client.get_cadip_client()
    catalog_client = generic_client.get_catalog_client()
    staging_client = generic_client.get_staging_client()
    dpr_client = generic_client.get_dpr_client()
    osam_client = generic_client.get_osam_client()

    print(f"Auxip service: {auxip_client.href_service}")
    print(f"PRIP service: {prip_client.href_service}")
    print(f"CADIP service: {cadip_client.href_service}")
    print(f"Catalog service: {catalog_client.href_service}")
    print(f"Staging service: {staging_client.href_service}")
    print(f"DPR service: {dpr_client.href_service}")
    print(f"OSAM service: {osam_client.href_service}")

    return (
        auxip_client,
        cadip_client,
        catalog_client,
        staging_client,
        prip_client,
    )


def get_or_create_test_collection(
    collection_id: str | None = None,
    description: str | None = None,
    temporal: TemporalExtent | None = None,
    title: str | None = None,
    stac_extensions: list[str] | None = None,
) -> CollectionClient:
    """Returns the given STAC collection or creates it if does not exist"""
    try:
        if (collection := catalog_client.get_collection(collection_id)) is not None:
            return collection
    except Exception as e:
        if "NotFoundError" in str(e):
            pass
        else:
            raise e
    return create_test_collection(
        collection_id,
        description,
        temporal,
        title,
        stac_extensions,
    )


def create_test_collection(
    collection_id: str | None = None,
    description: str | None = None,
    temporal: TemporalExtent | None = None,
    title: str | None = None,
    stac_extensions: list[str] | None = None,
) -> CollectionClient:
    """Create and return a test STAC collection"""

    if not collection_id:
        collection_id = TEST_COLLECTION
    # Clean the existing collection, if any
    catalog_client.remove_collection(collection_id)

    # Add new collection
    catalog_client.add_collection(
        Collection(
            id=collection_id,
            description=description,  # if None, rs-client will provide a default description for us
            title=title,  # if None, rs-client will provide a default title for us
            extent=Extent(
                spatial=SpatialExtent(bboxes=[-180.0, -90.0, 180.0, 90.0]),
                temporal=temporal or TemporalExtent([start_date, stop_date]),
            ),
            stac_extensions=stac_extensions,
        ),
    )

    # Return the inserted collection
    inserted_collection = catalog_client.get_collection(collection_id=collection_id)
    assert inserted_collection, "Collection was not inserted"
    return inserted_collection


def truncate_features_by_limit(item_collection, limit):
    """Truncate a response from a station to a limit of files"""
    # Load the dictionary from the file

    total_count = 0  # To keep track of the global count of assets
    truncated_features = []
    truncated_dict = item_collection.to_dict()

    for feature in truncated_dict["features"]:
        assets = feature.get("assets", {})
        asset_count = len(assets)

        if total_count + asset_count <= limit:
            total_count += asset_count
            truncated_features.append(feature)
        else:
            # Truncate assets in the current feature
            allowed_assets = limit - total_count
            feature["assets"] = dict(list(assets.items())[:allowed_assets])
            truncated_features.append(feature)
            break
    # Update the dictionary with the truncated features
    truncated_dict["features"] = truncated_features
    return ItemCollection.from_dict(truncated_dict)


def stage_test_objects(
    client,
    nb_of_objects,
    collection_id=None,
    objects_are_files=True,
    timestamp: DatetimeLike | None = None,
) -> ItemCollection:
    """Stage several files from cadip or auxip into the STAC catalog and return it."""

    catalog_collection_name = collection_id if collection_id else TEST_COLLECTION

    # The search method is based on a time interval
    item_collection = client.search(
        timestamp=timestamp if timestamp else [start_date, stop_date],
        max_items=nb_of_objects,
    )

    # for item in item_collection:
    #     if item.properties.get('datetime') > "2025":
    #     # Remove newly added S3 session
    #         item_collection.items.remove(item)
    assert isinstance(item_collection, ItemCollection)
    if objects_are_files:
        # truncate by number of files. In cadip case, the items are sessions which have more than one file
        item_collection = truncate_features_by_limit(item_collection, nb_of_objects)
    items_id = [item.id for item in item_collection]
    return stage_data(item_collection.to_dict(), items_id, catalog_collection_name)


def stage_data(
    staging_input: dict | str,
    items_id: list[str],
    catalog_collection_name: str,
    # timeout: int = 120,
) -> ItemCollection:
    """Stage an item collection into the STAC catalog and return it."""
    # Start the staging process. The catalog collection is either
    # provided, or the test collection created from create_test_collection() is used
    job_status = staging_client.run_staging(staging_input, catalog_collection_name)
    # NOTE: The timeout argument has been disabled, see the comment from rs-client-libraries
    # in ogcapi_client.wait_for_job function
    staging_client.wait_for_jobs(
        job_status,
        logger,
        # timeout,
        2,
    )
    time.sleep(0.5)
    return ItemCollection(
        list(catalog_client.get_items(catalog_collection_name, items_id)),
    )


def stage_single_item(
    item: Item,
    catalog_collection: ItemCollection,
) -> ItemCollection:
    """Stage a single item by converting it to an URL returning ItemCollection through the /search endpoint"""
    link = (
        item.get_links("root")[0].get_href()
        + "search?collections="
        + item.collection_id
        + "&limit=1&ids="
        + item.id
    )
    return stage_data(link, [item.id], catalog_collection.id)


def temporary_fix_adgs_feature(items_collection):
    # Disable instruments for moment
    for feature in items_collection["features"]:
        if "instruments" in feature["properties"]:
            del feature["properties"]["instruments"]
    # Update href and title
    for feature in items_collection["features"]:
        for asset in feature["assets"]:
            feature["assets"][asset]["title"] = asset
            feature["assets"][asset][
                "href"
            ] = f"http://mockup-station-adgs.processing.svc.cluster.local:8080/Products({feature['properties']['auxip:id']})/$value"
    return items_collection


########
# Init #
########


def init_demo(owner_id=None):
    """Init environment before running a demo notebook."""
    global apikey

    # In local mode, create the s3 buckets, if they do not already exists
    if local_mode:
        create_s3_buckets()

    # Init the prefect blocks
    init_prefect_blocks(_sync=True)

    # The API key should be set now
    if cluster_mode:
        apikey = os.getenv("RSPY_APIKEY")

    # Set OAuth2 authentication in the http request session
    if cluster_mode:
        http_session.cookies.set("session", os.environ["RSPY_OAUTH2_COOKIE"])

    # Default owner_id
    if not owner_id:
        owner_id = OWNER_ID

    # Init RsClient instances
    ret = init_rsclient(owner_id)

    # Save bucket credentials for the current user/owner
    save_bucket_credentials(osam_client, _sync=True)

    return ret
