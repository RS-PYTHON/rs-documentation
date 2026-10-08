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

import datetime
import time

import rs_client
from prefect import flow, get_run_logger
from rs_workflows.flow_utils import FlowEnv, FlowEnvArgs
from rs_workflows.record_flow_run import record_flow_run


@flow(name="record_flow_")
async def record_flow(
    env: FlowEnvArgs,
    flow_run_type: str = "systematic",
    mission: str = "sentinel-1",
    dpr_processor_name: str = "dpr_processor",
    dpr_processor_version: str = "dpr_processor_version",
    dpr_processor_unit: str = "dpr_processor_unit",
    dpr_processing_input_stac_items: str = "{'dpr_processing_input_stac_items': 'value'}",
):

    logger = get_run_logger()

    flow_env = FlowEnv(env)
    with flow_env.start_span(__name__, "init-pi-database"):
        record_flow_run.fn(start_date=datetime.datetime.now(), status="OK")

        logger.info("=== Flow started ===")
        logger.info(f"flow_run_type = {flow_run_type}")
        logger.info(f"mission = {mission}")
        logger.info(f"dpr_processor_name = {dpr_processor_name}")
        logger.info(f"dpr_processor_version = {dpr_processor_version}")
        logger.info(f"dpr_processor_unit = {dpr_processor_unit}")
        logger.info(
            f"dpr_processing_input_stac_items = {dpr_processing_input_stac_items}",
        )

        logger.info("Sleeping 10 seconds...")
        time.sleep(10)
        record_flow_run.fn(stop_date=datetime.datetime.now(), status="OK")
        logger.info("=== Flow finished ===")
