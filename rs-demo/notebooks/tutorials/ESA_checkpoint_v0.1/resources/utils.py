"""Utility Python module for the tutorials.

WARNING: AFTER EACH MODIFICATION, RESTART THE JUPYTER NOTEBOOK KERNEL !
"""

import boto3
import os

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

def create_s3_buckets(*buckets: list[str]):
    """Create a list of s3 buckets, if they do not already exists."""
    s3_client = get_s3_client()
    for bucket in buckets:
        try:
            s3_client.create_bucket(Bucket=bucket)
        except (s3_client.exceptions.BucketAlreadyExists, s3_client.exceptions.BucketAlreadyOwnedByYou):
            pass # do nothing if already exists