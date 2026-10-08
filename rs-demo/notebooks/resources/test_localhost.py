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
For testing: if we are running a Jupyter notebook from localhost, not from docker-compose,
then modify all the env vars to call the services from localhost.

Use with this at the top of your notebook:
import sys
sys.path.insert(0, "/path/to/parent/of/resources/dir")
import resources.test_localhost

Then in your notebook, select a Python kernel that you'll create like this:
python -m venv /PATH/TO/VENV
source /PATH/TO/VENV/bin/activate
pip install -U pip && \
pip install ipykernel psycopg2 && \
pip install -e /PATH/TO/rs-client-libraries && \
pip install \
    dask==2026.1.4 \
    dask-gateway==2025.4.0 \
    prefect[aws]==3.6.29 \
opentelemetry-bootstrap -a install
"""

import getpass
import os
from pathlib import Path

from dotenv import load_dotenv

THIS_DIR = Path(__file__).parent

# Read the .env file that contains env vars
load_dotenv(Path(__file__).parent.parent.parent / "local-mode" / ".env")

os.environ["RSPY_HOST_USER"] = getpass.getuser()

os.environ["RSPY_LOCAL_MODE"] = "1"
# rs-server urls
os.environ["RSPY_HOST_ADGS"] = "http://localhost:8001"
os.environ["RSPY_HOST_CADIP"] = "http://localhost:8002"
os.environ["RSPY_HOST_CATALOG"] = "http://localhost:8003"
os.environ["RSPY_HOST_STAGING"] = "http://localhost:8004"
os.environ["RSPY_HOST_PRIP"] = "http://localhost:8005"
os.environ["RSPY_HOST_DPR_SERVICE"] = "http://localhost:6003"
# s3 bucket
os.environ["S3_ENDPOINT"] = "http://localhost:9100"
os.environ["BUCKET_CONFIG_FILE_PATH"] = str(
    THIS_DIR.parent.parent / "local-mode/config/expiration_bucket.csv",
)
# postgres
os.environ["POSTGRES_HOST"] = "localhost"
# prefect
os.environ["PREFECT_URL"] = os.environ["RSPY_PREFECT_URL"] = "http://localhost:4200"
os.environ["PREFECT_API_URL"] = os.environ["PREFECT_URL"] + "/api"

os.environ["RSPY_OAUTH2_COOKIE"] = "dummy-cookie"
