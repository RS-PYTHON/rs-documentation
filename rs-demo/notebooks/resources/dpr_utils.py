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

"""Utility Python module for the Jupyter demos to run the DPR processors.

WARNING: AFTER EACH MODIFICATION, RESTART THE JUPYTER NOTEBOOK KERNEL !
"""

import glob
import shutil
import time
from datetime import timedelta
from os import path as osp
from pathlib import Path

from rs_client.ogcapi.dpr_client import ClusterInfo, DprClient, DprProcessor
from rs_common.logging import Logging
from rs_common.prefect_utils import (
    get_share_bucket,
    s3_delete,
    s3_download_dir,
    s3_upload_dir,
)

logger = Logging.default(__name__)


class DprDemo:
    """
    Run a DPR processor from a Jupyter demo notebook.
    """

    def __init__(
        self,
        owner_id: str,
        dpr_client: DprClient,
        local_config_dir: str | Path,
    ):
        """
        Constructor.

        Attributes:
            owner_id: user/owner ID
            dpr_client: rs-client-libraries DPR client instance
            local_config_dir: local config dir
            s3_config_dir: config dir in the S3 bucket
            s3_output_dir: default output dir in the s3 bucket
            s3_report_dir: default report dir in the s3 bucket
            s3_working_dir: default working dir in the s3 bucket
        """
        self.owner_id: str = owner_id
        self.dpr_client: DprClient = dpr_client
        self.local_config_dir: Path = Path(local_config_dir).absolute()
        self.s3_config_dir: str = ""
        self.s3_output_dir: str = ""
        self.s3_report_dir: str = ""
        self.s3_working_dir: str = ""

    async def init(self, local_secrets_file: str | Path | None):
        """
        Async initialization.

        Args:
            local_secrets_file: local eopf secrets.json file
        """
        # Get the prefect share bucket folder
        share_bucket, _ = await get_share_bucket()

        # s3 bucket dirs that will contain the data
        s3_base = osp.join(
            "s3://",
            share_bucket.bucket_name,
            share_bucket.bucket_folder,
            "users",
            self.owner_id,
        )
        self.s3_config_dir = osp.join(s3_base, "config")
        self.s3_output_dir = osp.join(s3_base, "output")
        self.s3_report_dir = osp.join(s3_base, "reports")
        self.s3_working_dir = osp.join(s3_base, "working")

        # Upload the local configuration dir to s3 bucket
        await s3_upload_dir(self.local_config_dir, self.s3_config_dir)

        # Update local secret file depending on the environment,
        # and upload it again to the s3 bucket.
        if local_secrets_file:
            local_secrets_file = Path(local_secrets_file).absolute()
            await self.dpr_client.update_configuration(
                local_path=local_secrets_file,
                s3_path=osp.join(
                    self.s3_config_dir,
                    str(local_secrets_file.relative_to(self.local_config_dir)),
                ),
            )

    async def run_process(
        self,
        process: DprProcessor,
        cluster_info: ClusterInfo,
        payload_subpath: str,
        s3_output_dir: str = "",
        s3_report_dir: str = "",
        del_s3_working_dir: str = "",
        experimental_config: dict = {},
        **kwargs,
    ):
        """
        Run the DPR processor.

        Args:
            process: processor to run
            cluster_info: Information to connect to a DPR Dask cluster
            payload_subpath: local eopf payload file, relative to the config dir
            s3_output_dir: output dir in the s3 bucket for this run. Will be removed before the run.
            s3_report_dir: report dir in the s3 bucket for this run. Will be removed before the run.
            del_s3_working_dir: working dir in the s3 bucket for this run. If given, it will be removed before the run.
            experimental_config: experimental DPR processor configuration, used only for testing.
            kwargs: Specific environment variables to expand in the payload file
        """
        # Use default values
        if not s3_output_dir:
            s3_output_dir = self.s3_output_dir
        if not s3_report_dir:
            s3_report_dir = self.s3_report_dir

        print(f"s3_config_dir: {self.s3_config_dir}")
        print(f"payload_subpath: {payload_subpath}")
        print(f"Remove s3_output_dir: {s3_output_dir}")
        print(f"Remove s3_report_dir: {s3_report_dir}")

        # Remove existing output and report folders
        s3_delete(s3_output_dir, log=True)
        s3_delete(s3_report_dir, log=True)

        # Remove working dir, if given
        if del_s3_working_dir:
            print(f"Remove s3_working_dir: {del_s3_working_dir}")
            s3_delete(del_s3_working_dir, log=True)

        # Update local payload file depending on the environment, upload it to the s3 bucket,
        # and initialize output bucket folders.
        await self.dpr_client.update_configuration(
            local_path=osp.join(str(self.local_config_dir), payload_subpath),
            s3_path=osp.join(self.s3_config_dir, payload_subpath),
            is_payload=True,
            # Specific environment variables to expand in the payload file
            **kwargs,
        )

        # Run processor
        start_time = time.time()
        result = self.dpr_client.run_process(
            process,
            cluster_info,
            s3_config_dir=self.s3_config_dir,
            payload_subpath=payload_subpath,
            s3_report_dir=s3_report_dir,
            extra_data={"experimental_config": experimental_config},
        )
        try:
            self.dpr_client.wait_for_job(result, logger=logger, poll_interval=5)
        finally:
            print(
                f"Processor execution time: {str(timedelta(seconds=time.time() - start_time))}",
            )

            # Download reports folder from the s3 bucket
            local_report_dir = f"./reports/{Path(s3_report_dir).name}"
            shutil.rmtree(local_report_dir, ignore_errors=True)
            await s3_download_dir(s3_report_dir, local_report_dir)

            # Display logs here
            local_log_file = glob.glob(
                osp.join(local_report_dir, "**/*.processor.log"),
                recursive=True,
            )
            if local_log_file:
                local_log_file = local_log_file[0]
                with open(local_log_file, encoding="utf-8") as openend:
                    print(f"Log file {local_log_file!r}:\n{openend.read()}")
            else:
                print(f"No processor log file was uploaded under: {local_report_dir!r}")

        print(f"Output product generated on: {s3_output_dir!r}")
