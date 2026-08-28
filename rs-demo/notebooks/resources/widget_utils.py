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

"""Widgets used in the Jupyter notebooks.

WARNING: AFTER EACH MODIFICATION, RESTART THE JUPYTER NOTEBOOK KERNEL !
"""

import asyncio
import inspect
import json
import os
import re
import subprocess
import sys
from contextlib import chdir
from importlib import reload
from os import path as osp
from pathlib import Path
from runpy import run_path

import ipywidgets as widgets
import prefect
import rs_workflows
import yaml
from prefect.client.orchestration import get_client
from prefect.client.schemas.objects import FlowRun
from prefect.flows import Flow, State
from resources import utils
from rs_client.ogcapi.dpr_client import DprProcessor
from rs_common import prefect_utils
from rs_workflows.flow_utils import AdfType

#
# Jupyter doc: https://ipywidgets.readthedocs.io/en/latest/examples/Widget%20List.html
#

########################
# Choose DPR processor #
########################

dpr_proc_radio = widgets.RadioButtons(
    options=[("MOCKUP", "mockup")] + [(proc.name, proc.value) for proc in DprProcessor],
    value="mockup",
    description="DPR processor in this demo:",
    indent=False,
)


def get_pipeline_unit_radio():
    """Return radio buttons to chosse the DPR processor pipeline or processing unit"""
    # Avaiable pipelines and processing units
    pipelines = []
    units = ["single_unit"]

    match dpr_proc_radio.value:
        case "mockup":
            pipelines = ["mockup_full"]
        case DprProcessor.S1L0.value:
            pipelines = ["s1_l0_full"]
        case DprProcessor.S3L0.value:
            pipelines = ["s3_l0_full"]
        case DprProcessor.S1ARD.value:
            pipelines = ["s1_ard_full"]
            units = [
                "calibration",
                "reference_dem",
                "reference_geometry",
                "coregistration",
                "geocoding",
                "mosaicking",
            ]
        case DprProcessor.S3L1OLCI.value:
            pipelines = ["ol1_eo"]

    # Text and dict entry used in radio buttons for each pipeline or unit
    options = []
    for p in pipelines:
        options.append((f"{p} (pipeline) ", {"pipeline": p, "unit": ""}))
    for u in units:
        options.append((f"{u} (unit)", {"pipeline": "", "unit": u}))

    return widgets.RadioButtons(
        options=options,
        description=f"Run {dpr_proc_radio.value!r} full pipeline or single processing unit:",
        indent=False,
    )


########################
# Choose ADF type #
########################

adf_proc_radio = widgets.RadioButtons(
    options=[(adf_type.name, adf_type.value) for adf_type in AdfType],
    description="ADF type in this demo:",
    indent=False,
)

########################
# Deploy Prefect flows #
########################

# Deploy prefect flow from a YAML deployment file or using the S3 bucket ?
# The goal is to use the yaml file which itself should use the rs-client-libraries git repo and
# "develop" branch but it's hard to test changes in a new branch.
# So during development it's easier to deploy your local changes using a bucket.
deploy_prefect_radio = widgets.RadioButtons(
    options=[
        ("Yaml file and git repository", "yaml"),
        ("Local source code and s3 bucket", "bucket"),
        ("Do nothing", "nothing"),
    ],
    value="bucket" if utils.local_mode else "yaml",
    description="Deploy Prefect flows using:",
    indent=False,
)


async def deploy_prefect(
    deploy_file: str,
    s3_code_folder: str,
    work_pool_name: str,
) -> tuple[str] | str:
    """
    Deploy the Prefect flows that are implemented in the `rs-client-libraries` git repository.

    WARNING: the `rs-client-libraries` source code must be identical in these 3 environments:

    * https://github.com/RS-PYTHON/rs-demo.git (if we deploy using git)
    * This Jupyter environment
    * The Prefect Docker images

    Args:
        deploy_file: Prefect YAML deployment file path.
        s3_code_folder: S3 bucket folder where to deploy the source code.
        work_pool_name: prefect workpool name.

    Returns:
        Deployed flow name(s).
    """
    deployments = []
    deployed_names = []
    deploy_file = osp.realpath(deploy_file)

    # Parent folder of the rs-client-libraries workflows
    rs_workflows_parent = Path(rs_workflows.__path__[0]).parent.absolute()

    print(f"Read Prefect deployment file: {deploy_file!r}")
    with open(deploy_file, encoding="utf-8") as opened:
        deploy_contents = yaml.safe_load(opened)

    # Read deployment info from yaml file
    for deployment in deploy_contents.get("deployments", []):
        try:
            name = deployment["name"]
            tags = deployment["tags"]
            entrypoint = deployment["entrypoint"]

            # The entrypoint should be something like <module_path>:<python_func>
            module, flow = entrypoint.split(":")

            # Read the entrypoint python module
            with chdir(rs_workflows_parent):
                flow_name = run_path(module)[flow].name

            # The deployed flow name is <flow_name>/<deployment_name>
            deployed_names.append(f"{flow_name}/{name}")

            # Save deployment info
            deployments.append((name, tags, entrypoint))

        except Exception as e:
            raise RuntimeError(
                f"Error reading deployment: {json.dumps(deployment, indent=2)}",
            ) from e

    # Deploy using the yaml file, from the rs_workflow parent folder.
    # It should use the git repositry and 'develop' branch.
    if deploy_prefect_radio.value == "yaml":
        print(f"Deploy from file:")
        cmd = [
            "prefect",
            "--no-prompt",
            "deploy",
            "--prefect-file",
            deploy_file,
            "--all",
        ]
        print(f"""cd {str(rs_workflows_parent)!r}; '{"' '".join(cmd)}'""")
        with chdir(rs_workflows_parent):
            subprocess.run(cmd)

    # Deploy local source code using the S3 bucket and pure python calls.
    elif deploy_prefect_radio.value == "bucket":

        # Local source code
        local_path = osp.realpath(rs_workflows.__path__[0])

        # Use a specific prefect block on the bucket for this subfolder
        code_bucket, _ = await prefect_utils.get_share_bucket(s3_code_folder)
        print(
            f"Deploy flows from {local_path!r} to 's3://{code_bucket.bucket_name}/{code_bucket.bucket_folder}'",
        )

        # Upload local workflows package contents, then the client and config folders
        await code_bucket.put_directory(local_path=local_path, to_path="rs_workflows")
        await code_bucket.put_directory(
            local_path=osp.realpath(osp.join(local_path, "..", "rs_client")),
            to_path="rs_client",
        )

        # Also upload the config folder
        local_config = osp.realpath(osp.join(local_path, "..", "config"))
        await code_bucket.put_directory(local_path=local_config, to_path="config")

        # Reload all rs-client-libraries modules
        for module in list(sys.modules.values()):
            if any(
                module.__name__.startswith(prefix)
                for prefix in ["rs_client.", "rs_common.", "rs_workflows."]
            ):
                reload(module)

        # Deploy the flows
        for deployment in deployments:
            name, tags, entrypoint = deployment
            flow = await prefect.flow.from_source(
                source=code_bucket,
                entrypoint=entrypoint,
            )
            await flow.deploy(
                name=name,
                work_pool_name=work_pool_name,  # note: we could try to read it from the yaml file instead
                tags=tags,
                ignore_warnings=True,
            )

    # Wait for deployments
    if deploy_prefect_radio.value != "nothing":
        for deployed_name in deployed_names:
            await prefect_utils.wait_for_deployment(deployed_name)

    return deployed_names[0] if (len(deployed_names) == 1) else deployed_names


#####################
# Run Prefect flows #
#####################

# Run Prefect flows by either:
# - using the commande line (this is the regular usage)
# - calling directly the python code (faster and allows to debug with breakpoints)
run_prefect_radio = widgets.RadioButtons(
    options=[
        ("'prefect deployment run' command line", "cmd"),
        ("Pure python code", "python"),
        ("Do nothing (I'll use the prefect UI)", "nothing"),
    ],
    value="cmd",
    description="Run Prefect flows using:",
    indent=False,
)


async def run_prefect(
    deploy_name: str,
    py_func: Flow | None,
    params: dict,
    flow_run_name: str | None = None,
) -> State | None:
    """Run prefect flow"""

    deployment_url = f"{os.environ['RSPY_PREFECT_URL']}/deployments"
    print(
        f"Call flow {deploy_name!r} from {deployment_url} with:{json.dumps(params, indent=2)}",
    )

    if run_prefect_radio.value == "nothing":
        return None

    # Using command line
    if run_prefect_radio.value == "cmd":
        return await run_prefect_flow_cmd(deploy_name, params, flow_run_name)

    # By calling directly the python code
    elif py_func:
        return await run_prefect_flow_python(py_func, params)

    else:
        return None


async def run_prefect_flow_cmd(
    deploy_name: str,
    params: dict,
    flow_run_name: str | None = None,
) -> State | None:
    """Run prefect flow using command line"""
    cmd = [
        "prefect",
        "deployment",
        "run",
        deploy_name,
        "--params",
        json.dumps(params),
        "--watch",
    ]
    if flow_run_name:
        cmd.extend(["--flow-run-name", flow_run_name])
    print(f"""Run flow from command line:\n'{"' '".join(cmd)}'""")
    flow_run_id = None
    uuid_regex = re.compile(r"UUID:\s*([0-9a-fA-F-]{36})")

    process = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT,
    )

    async for raw_line in process.stdout:
        line = raw_line.decode()
        print(line, end="")  # keep standard output
        if flow_run_id is None:
            match = uuid_regex.search(line)
            if match:
                flow_run_id = match.group(1)

    returncode = await process.wait()

    if flow_run_id is None:
        raise RuntimeError(
            f"Unable to extract flow_run_id from Prefect CLI output (return code: {returncode})",
        )

    async with get_client() as client:
        flow_run = await client.read_flow_run(flow_run_id)

    return flow_run.state


async def run_prefect_flow_python(py_func: Flow, params: dict) -> State | None:
    """Run prefect flow by calling directly the python code"""
    print("Run flow from python code")
    # Reload all rs-client-libraries modules
    for module in list(sys.modules.values()):
        if any(
            module.__name__.startswith(prefix)
            for prefix in ["rs_client.", "rs_common.", "rs_workflows."]
        ):
            reload(module)

    # Make sure to call the python function from its reloaded module
    module = inspect.getmodule(py_func)
    py_func = getattr(module, py_func.fn.__name__)

    def custom_completion(flow: Flow, _flow_run: FlowRun, state: State):
        """On completion, save the state as a Flow instance field"""
        flow.custom_state = state

    py_func.on_completion(custom_completion)

    # Call the python function
    await py_func(**params)

    # py_func is a Flow instance that has been updated with its last state
    return py_func.custom_state
