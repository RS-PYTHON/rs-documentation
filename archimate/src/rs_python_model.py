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

"""RS-Python architecture model: elements, relationships and the six views of the Architecture Dossier."""

from model_builder import Builder
from rs_python_elements import elements
from rs_python_views import (
    context_view,
    detailed_application_view,
    functional_view,
    hl_application_view,
    infrastructure_view,
    network_view,
)

VERSION = "RS-Python v1.x (reference platform ops.rs-python.eu)"


def build() -> Builder:
    """Build the model; the relationships are checked against the ArchiMate rules by pyArchimate."""
    m = Builder(
        "RS-Python - Architecture",
        "Architecture of RS-Python, the Copernicus Reference System Python, deployed on OVHcloud. Built from the "
        "RS-PYTHON GitHub organisation (https://github.com/RS-PYTHON) and the online documentation "
        "(https://home.rs-python.eu/rs-documentation/). ArchiMate 3.2 notation.",
    )
    m.model.prop("ArchiMate version", "3.2")
    m.model.prop("Scope", VERSION)
    elements(m)
    context_view(m)
    functional_view(m)
    hl_application_view(m)
    detailed_application_view(m)
    infrastructure_view(m)
    network_view(m)
    return m
