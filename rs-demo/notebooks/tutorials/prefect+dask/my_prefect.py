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

"""Python module for the tutorials, to be shared with the prefect workers.

Implement utility functions and prefect tasks and flows.

WARNING: AFTER EACH MODIFICATION, RESTART THE JUPYTER NOTEBOOK KERNEL !
"""

import importlib
import json
import logging
import os
import random
from pathlib import Path

from prefect import flow, get_run_logger, task
from rs_common.prefect_utils import get_ip_address

# NOTE: the main code outside the functions is run by both the client and prefect workers.
# But this log won't show when run from a prefect worker because get_run_logger() is not available yet.
logging.warning(
    f"Hello from {os.environ['HELLO_FROM']!r} {get_ip_address()!r} (main code)",
)
# You can test to write an empty file to check that it is written
# on both the client and prefect workers filesystems.
Path("/tmp/.empty").touch()


#
# Quickstart flow and tasks from: https://docs.prefect.io/v3/get-started/quickstart
#


@flow(log_prints=True)
def flow_show_stars(github_repos: list[str], test_pip: str | None = None):
    """Flow: Show the number of stars that GitHub repos have"""
    logger = get_run_logger()
    logger.warning(
        f"Hello from {os.environ['HELLO_FROM']!r} {get_ip_address()!r} (flow)",
    )

    # Test that "pip install xxx" was run in the worker container
    if test_pip:
        importlib.import_module(test_pip)

    for repo in github_repos:
        # Call Task 1
        repo_stats = task_fetch_stats(repo)

        # Call Task 2
        stars = task_get_stars(repo_stats)

        # Print the result
        logger.warning(f"Result for repository {repo!r}: {stars} stars")


@task
def task_fetch_stats(github_repo: str):
    """Task 1: Fetch the statistics for a GitHub repo"""
    logger = get_run_logger()
    logger.warning(
        f"Hello from {os.environ['HELLO_FROM']!r} {get_ip_address()!r} (task_fetch_stats)",
    )
    # return httpx.get(f"https://api.github.com/repos/{github_repo}").json()
    # Mock the call to github to avoid flooding them
    return {"github_repo": github_repo, "stargazers_count": random.randint(100, 1000)}


@task
def task_get_stars(repo_stats: dict):
    """Task 2: Get the number of stars from GitHub repo statistics"""
    logger = get_run_logger()
    logger.warning(
        f"Hello from {os.environ['HELLO_FROM']!r} {get_ip_address()!r} (task_fetch_stats)",
    )
    try:
        return repo_stats["stargazers_count"]
    except KeyError:
        logger.error(
            f"'stargazers_count' not found in:\n{json.dumps(repo_stats, indent=2)}",
        )
        raise
