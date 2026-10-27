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

"""RS-Python architecture model: the six views of the Architecture Dossier."""

from model_builder import (
    CONTAINER_APP,
    CONTAINER_TECH,
    EXT_IFACE,
    EXTERNAL,
    SOI,
    Builder,
    ViewBuilder,
)
from rs_python_elements import FUNCTIONAL_PACKAGES

# Names of relationships used several times
FLOW_RUNS = "flow runs"
HTTPS_443 = "HTTPS 443"
NFS = "NFS 2049/tcp"

# =================================================================================================================
# 1. System in Context
# =================================================================================================================


def context_view(m: Builder):
    """View 1: System in Context."""
    v = m.view(
        "context",
        "1. System in Context",
        "Layered",
        "RS-Python as a black box: the services it provides, the user roles that consume them, the external "
        "systems that interact with it and the providers it relies on.",
    )
    # roles
    roles = [
        ("r_user", "search, stage, catalog, download, processing, flows"),
        ("r_dev", "virtual environment, flows, processing"),
        ("r_op", "flow supervision, monitoring"),
        ("r_admin", "accounts & rights, deployment, monitoring"),
        ("r_sec", "security monitoring"),
    ]
    soi_x, soi_w = 700, 920
    centers = [soi_x + 120 + i * 170 for i in range(5)]
    for (k, _), c in zip(roles, centers):
        v.add(k, c - 80, 30, 160, 60)
    # SOI with the services it realizes
    v.add("c_soi", soi_x, 200, soi_w, 480, fill=SOI, font_size=13)
    services = [
        "s_search",
        "s_staging",
        "s_catalog",
        "s_access",
        "s_processing",
        "s_orchestration",
        "s_venv",
        "s_admin",
    ]
    for i, s in enumerate(services):
        v.add(s, soi_x + 50 + (i % 2) * 440, 270 + (i // 2) * 95, 380, 60, parent="c_soi", nest="Realization")
    for (k, label), c in zip(roles, centers):
        v.serve("c_soi", k, label, bend=[(c, 192)])

    # external data sources (left)
    v.add("e_sentinel", 20, 240, 160, 60)
    v.add("g_csc", 250, 200, 280, 290, fill=EXTERNAL)
    v.add("x_cadip", 280, 240, 220, 55, parent="g_csc", nest="Aggregation", fill=EXTERNAL)
    v.add("x_auxip", 280, 320, 220, 55, parent="g_csc", nest="Aggregation", fill=EXTERNAL)
    v.add("x_prip", 280, 400, 220, 55, parent="g_csc", nest="Aggregation", fill=EXTERNAL)
    v.add("g_dataspaces", 250, 515, 280, 170, fill=EXTERNAL)
    v.add("x_cdse", 280, 550, 220, 55, parent="g_dataspaces", nest="Aggregation", fill=EXTERNAL)
    v.add("x_edh", 280, 620, 220, 55, parent="g_dataspaces", nest="Aggregation", fill=EXTERNAL)
    v.flow("e_sentinel", "x_cadip", "downlink (CADU)")
    for k, label, y in (
        ("x_cadip", "raw data sessions (OData / HTTPS)", 267),
        ("x_auxip", "auxiliary data files (OData / HTTPS)", 347),
        ("x_prip", "L0, L1, L2 products (OData / HTTPS)", 427),
        ("x_cdse", "products & ADF (STAC API, S3)", 577),
        ("x_edh", "Copernicus DEM (STAC API)", 647),
    ):
        v.flow(k, "c_soi", label, bend=[(680, y)])

    # hosting provider (right)
    v.add("g_ovh", 1830, 200, 280, 480, fill=EXTERNAL)
    for i, (k, label) in enumerate(
        (
            ("ts_mks", "container hosting"),
            ("ts_s3", "product & backup storage"),
            ("ts_registry", "private images"),
            ("ts_iaas", "bastion, load balancer, network"),
        ),
    ):
        y = 245 + i * 85
        v.add(k, 1860, y, 220, 60, parent="g_ovh", nest="Aggregation", fill=EXTERNAL)
        v.serve(k, "c_soi", label, bend=[(1650, y + 30)])
    v.add("x_ovhapi", 1860, 590, 220, 60, parent="g_ovh", nest="Aggregation", fill=EXTERNAL)
    v.flow("c_soi", "x_ovhapi", "S3 accounts & access policies", bend=[(1650, 620)])

    # software supply chain (bottom)
    v.add("g_supply", 780, 740, 760, 120, fill=EXTERNAL)
    v.add("x_github", 820, 780, 300, 60, parent="g_supply", nest="Aggregation", fill=EXTERNAL)
    v.add("x_gitlab", 1200, 780, 300, 60, parent="g_supply", nest="Aggregation", fill=EXTERNAL)
    v.flow("x_github", "c_soi", "Docker images, Helm charts, Python packages", bend=[(970, 700)])
    v.flow("x_gitlab", "c_soi", "DPR processors & CPM, CI jobs", bend=[(1350, 700)])
    v.add("a_eopf", 1250, 910, 200, 55)
    v.connect("Association", "a_eopf", "x_gitlab", "develops")
    v.note(
        "System of Interest in blue (black box) with the services it provides; external systems and providers "
        "in grey. Roles are served by the System of Interest (labels: services used).",
        20,
        740,
        330,
        85,
    )


# =================================================================================================================
# 2. Functional Top-Level Decomposition
# =================================================================================================================


def functional_view(m: Builder):
    """View 2: Functional Top-Level Decomposition."""
    v = m.view(
        "functional",
        "2. Functional Top-Level Decomposition",
        "Service Realization",
        "Functional packages of RS-Python (application functions) and their functions (nested: composition). "
        "Each package realizes the RS-Python services it supports. The components assigned to each package "
        "are listed in the documentation of the package.",
    )
    pitch, top, height = 214, 170, 40 + 6 * 54 + 10
    for i, package in enumerate(FUNCTIONAL_PACKAGES):
        v.add(package.key, 20 + i * pitch, top, 200, height, fill=CONTAINER_APP)
        for j, _ in enumerate(package.functions):
            v.add(f"{package.key}_{j}", 30 + i * pitch, top + 45 + j * 54, 180, 46, parent=package.key)
        if package.services[0] not in v.by_element:
            # service above its main package, Platform Administration centered above FP8 and FP9
            shift = pitch // 2 if package.services[0] == "s_admin" else 0
            v.add(package.services[0], 25 + i * pitch + shift, 30, 190, 60)
    for package in FUNCTIONAL_PACKAGES:
        for k, s in enumerate(package.services):
            bend = [(v.by_element[package.key].x + 160, 130)] if k else ()
            v.connect("Realization", package.key, s, bend=bend)
    v.note(
        "Functional packages and functions are application functions (nesting = composition). Dotted arrows: "
        "realization of the RS-Python services. Allocation of the components: see the table of the dossier.",
        20,
        top + height + 20,
        640,
        50,
    )


# =================================================================================================================
# 3. High Level Application View
# =================================================================================================================

HL_COLS = [400 + i * 215 for i in range(8)]  # column centres of the high level application view


def box(cx: float, w: float) -> int:
    """Left of a box of width w centred on cx."""
    return int(cx - w / 2)


def hl_application_view(m: Builder):
    """View 3: High Level Application View."""
    v = m.view(
        "hl-application",
        "3. High Level Application View",
        "Layered",
        "Application components of RS-Python and their information flows, between themselves, with the "
        "user roles (through the external interfaces, in orange) and with the external systems (in grey).",
    )
    # System of Interest
    v.add("c_soi", 260, 150, 1760, 730, fill=CONTAINER_APP, font_size=13)
    # external interfaces (top edge) and user-facing components (tier A)
    top = [
        ("i_stacb", "c_stacb", 0),
        ("i_web", None, 1),
        ("i_apikey", "c_apikey", 2),
        ("i_keycloak", "c_keycloak", 3),
        ("i_jupyter", "c_jupyter", 4),
        ("i_prefect", "c_prefect", 5),
        ("i_grafana", "c_monitoring", 6),
        ("i_security", "c_security", 7),
    ]
    for iface, c, col in top:
        v.add(iface, box(HL_COLS[col], 170), 175, 170, 55, parent="c_soi", fill=EXT_IFACE)
        if c:
            v.add(c, box(HL_COLS[col], 170), 300, 170, 65, parent="c_soi")
    # tier B and C
    v.add("c_web", box(HL_COLS[1], 230), 455, 230, 80, parent="c_soi")
    v.add("c_daskgw", box(HL_COLS[4], 170), 460, 170, 60, parent="c_soi")
    v.add("c_flows", box(HL_COLS[5], 170), 455, 170, 70, parent="c_soi")
    v.add("c_dask", box(HL_COLS[4], 170), 630, 170, 80, parent="c_soi")
    v.add("c_gitlab_runner", box(HL_COLS[7], 170), 630, 170, 60, parent="c_soi")
    m.el("g_data", "Grouping", "Data")
    v.add("g_data", 285, 600, 230, 255, parent="c_soi", nest="Aggregation")
    v.add("d_stac", 300, 640, 200, 60, parent="g_data", nest="Aggregation")
    v.add("d_products", 300, 740, 200, 75, parent="g_data", nest="Aggregation")
    for iface, c, _ in top:
        v.connect("Composition", c or "c_web", iface)

    # roles
    v.add("r_user", box(HL_COLS[1], 160), 25, 160, 55)
    v.add("r_admin", box(HL_COLS[3], 160), 25, 160, 55)
    v.add("r_dev", box((HL_COLS[4] + HL_COLS[5]) / 2, 160), 25, 160, 55)
    v.add("r_op", box((HL_COLS[5] + HL_COLS[6]) / 2, 160), 25, 160, 55)
    v.add("r_sec", box(HL_COLS[7], 160), 25, 160, 55)
    # object storage (technology) and OVHcloud API, on the left
    v.add("x_ovhapi", 20, 465, 190, 60, fill=EXTERNAL)
    v.add("n_s3", 20, 600, 200, 130)
    m.el(
        "i_s3",
        "TechnologyInterface",
        "S3 API (HTTPS)",
        "S3 API of the OVHcloud Object Storage: direct access to the buckets with the personal S3 credentials, "
        "or download with pre-signed URLs.",
    )
    v.add("i_s3", 35, 655, 170, 50, parent="n_s3", fill=EXT_IFACE)
    _hl_application_view_flows(v)


def _hl_application_view_flows(v: ViewBuilder):
    """Flows of the view."""
    # role flows
    v.flow("r_user", "i_stacb", "product browsing")
    v.flow("r_user", "i_web", "searches, jobs, S3 credentials")
    v.flow("r_user", "i_apikey", "API keys")
    v.flow("r_user", "i_prefect", FLOW_RUNS, bend=[(700, 95), (HL_COLS[5], 95)])
    v.flow("r_user", "i_s3", "product download", bend=[(235, 52), (235, 680)])
    v.flow("r_admin", "i_keycloak", "users & roles")
    v.flow("r_dev", "i_jupyter", "notebooks, custom flows")
    v.flow("r_dev", "i_prefect", "flow deployments")
    v.flow("r_op", "i_prefect", "flow supervision")
    v.flow("r_op", "i_grafana", "logs, metrics, traces, PI")
    v.flow("r_sec", "i_security", "security events")

    # internal flows
    v.flow("c_stacb", "c_web", "STAC requests")
    v.flow("c_web", "c_apikey", "API key validation")
    v.flow("c_web", "c_keycloak", "token validation, users & roles (OSAM)")
    v.flow("c_jupyter", "c_daskgw", "cluster management")
    v.flow("c_prefect", "c_flows", FLOW_RUNS)
    v.flow(
        "c_flows",
        "c_web",
        "search, staging, catalog & processing requests",
        bend=[(HL_COLS[5] - 45, 600), (680, 600)],
    )
    v.flow("c_web", "c_dask", "staging tasks, processor runs", bend=[(900, 670)])
    v.flow("c_daskgw", "c_dask", "cluster creation & scaling")
    v.connect("Access", "c_web", "d_stac", access="ReadWrite")
    v.connect("Access", "c_web", "d_products", access="ReadWrite", bend=[(560, 762)])
    v.connect("Access", "c_dask", "d_products", access="ReadWrite", bend=[(HL_COLS[4], 795)])
    v.connect("Association", "n_s3", "d_products", "stores")
    v.flow("c_web", "x_ovhapi", "S3 accounts & access policies")

    # external systems
    v.add("g_csc", 500, 910, 560, 110, fill=EXTERNAL)
    for i, k in enumerate(("x_cadip", "x_auxip", "x_prip")):
        v.add(k, 520 + i * 180, 950, 160, 55, parent="g_csc", nest="Aggregation", fill=EXTERNAL)
    v.add("g_dataspaces", 1180, 910, 400, 110, fill=EXTERNAL)
    v.add("x_cdse", 1200, 950, 180, 55, parent="g_dataspaces", nest="Aggregation", fill=EXTERNAL)
    v.add("x_edh", 1390, 950, 170, 55, parent="g_dataspaces", nest="Aggregation", fill=EXTERNAL)
    v.add("x_gitlab", box(HL_COLS[7], 170), 940, 170, 55, fill=EXTERNAL)
    v.flow("g_csc", "c_web", "sessions, ADF & product metadata (OData)", bend=[(HL_COLS[1], 895)])
    v.flow("g_csc", "c_dask", "product files (HTTPS)")
    v.flow("g_dataspaces", "c_flows", "ADF & DEM metadata (STAC)", bend=[(HL_COLS[5], 895)])
    v.flow("g_dataspaces", "c_dask", "CDSE products (S3)")
    v.flow("x_gitlab", "c_gitlab_runner", "CI jobs (CPM tests)")
    v.note(
        "All the web UIs authenticate the users with Keycloak (OAuth2 / OIDC); scripts and flows use API keys.\n"
        "All the components send their logs, metrics and OpenTelemetry traces to the monitoring stack.",
        HL_COLS[6] - 85,
        450,
        400,
        75,
        parent="c_soi",
    )
    v.note(
        "Orange: external interfaces of RS-Python, exposed in HTTPS by the Envoy Gateway load balancer. "
        "Grey: external systems.",
        20,
        760,
        200,
        95,
    )


# =================================================================================================================
# 4. Detailed Application View
# =================================================================================================================


def detailed_application_view(m: Builder):
    """View 4: Detailed Application View."""
    v = m.view(
        "detailed-application",
        "4. Detailed Application View",
        "Layered",
        "Detailed application components of RS-Python (micro-services, virtual environment, IAM, monitoring), "
        "their interfaces (external ones in orange), their data and their information flows.",
    )
    # top row
    v.add("c_stacb", 390, 20, 270, 120)
    v.add("i_stacb", 415, 80, 220, 45, parent="c_stacb", fill=EXT_IFACE)
    v.add("x_ovhapi", 720, 40, 200, 60, fill=EXTERNAL)
    v.add("d_bucketcfg", 1060, 40, 170, 60)
    v.add("d_users", 1430, 40, 180, 60)
    v.add("d_apikeys", 1770, 40, 180, 60)

    # rs-server and rs-dpr-service
    v.add("c_web", 360, 170, 960, 520, fill=CONTAINER_APP)
    services = [
        ("c_cadip", "i_cadip", 390, 215),
        ("c_adgs", "i_auxip", 390, 365),
        ("c_prip", "i_prip", 390, 515),
        ("c_frontend", "i_docs", 700, 215),
        ("c_staging", "i_staging", 700, 515),
        ("c_osam", "i_osam", 1010, 215),
        ("c_catalog", "i_catalog", 1010, 365),
        ("c_dpr", "i_dpr", 1010, 515),
    ]
    for c, i, x, y in services:
        v.add(c, x, y, 270, 120, parent="c_web")
        v.add(i, x + 25, y + 68, 220, 40, parent=c, fill=EXT_IFACE)
    m.rel("Composition", "i_web", "i_docs")
    for i in ("i_cadip", "i_auxip", "i_prip", "i_catalog", "i_staging", "i_osam", "i_dpr"):
        m.rel("Composition", "i_web", i)

    # external data sources
    v.add("g_csc", 20, 190, 250, 470, fill=EXTERNAL)
    for k, y in (("x_cadip", 245), ("x_auxip", 395), ("x_prip", 545)):
        v.add(k, 45, y, 200, 60, parent="g_csc", nest="Aggregation", fill=EXTERNAL)
    v.flow("x_cadip", "c_cadip", "sessions & files (OData)")
    v.flow("x_auxip", "c_adgs", "ADF metadata (OData)")
    v.flow("x_prip", "c_prip", "products metadata (OData)")

    # jobs, Dask clusters, products
    v.add("d_jobs", 915, 712, 150, 55)
    v.add("c_dask", 360, 800, 960, 160, fill=CONTAINER_APP)
    v.add("c_dask_staging", 700, 845, 270, 90, parent="c_dask")
    v.add("c_dask_dpr", 1010, 845, 270, 90, parent="c_dask")
    v.add("d_products", 900, 1010, 300, 65)

    # IAM column
    v.add("c_keycloak", 1420, 215, 200, 120)
    v.add("i_keycloak", 1430, 275, 180, 50, parent="c_keycloak", fill=EXT_IFACE)
    v.add("d_stac", 1430, 395, 180, 60)
    v.add("c_daskgw", 1420, 820, 200, 120)
    v.add("i_dask", 1430, 875, 180, 55, parent="c_daskgw", fill=EXT_IFACE)
    _detailed_application_view_right(v)
    _detailed_application_view_flows(v)


def _detailed_application_view_right(v: ViewBuilder):
    """Virtual environment column of the view."""
    # virtual environment column
    v.add("c_apikey", 1720, 215, 280, 120)
    v.add("i_apikey", 1745, 275, 230, 50, parent="c_apikey", fill=EXT_IFACE)
    v.add("c_jupyter", 1720, 385, 280, 110)
    v.add("i_jupyter", 1745, 440, 230, 45, parent="c_jupyter", fill=EXT_IFACE)
    v.add("c_prefect", 1720, 540, 280, 280, fill=CONTAINER_APP)
    v.add("c_prefect_server", 1735, 580, 250, 100, parent="c_prefect")
    v.add("i_prefect", 1750, 630, 220, 42, parent="c_prefect_server", fill=EXT_IFACE)
    v.add("c_prefect_workers", 1735, 740, 250, 60, parent="c_prefect")
    v.add("c_flows", 1720, 870, 280, 80)
    v.add("g_dataspaces", 1700, 1000, 320, 120, fill=EXTERNAL)
    v.add("x_cdse", 1715, 1045, 145, 60, parent="g_dataspaces", nest="Aggregation", fill=EXTERNAL)
    v.add("x_edh", 1870, 1045, 135, 60, parent="g_dataspaces", nest="Aggregation", fill=EXTERNAL)

    # data / runner column
    v.add("d_prefectdb", 2060, 600, 180, 60)
    v.add("d_pi", 2060, 840, 180, 50)
    v.add("d_quota", 2060, 910, 180, 50)
    v.add("c_gitlab_runner", 2060, 1000, 180, 70)
    v.add("x_gitlab", 2060, 1120, 180, 60, fill=EXTERNAL)

    # monitoring and security
    v.add("c_monitoring", 2300, 170, 360, 450, fill=CONTAINER_APP)
    v.add("c_alloy", 2320, 230, 320, 55, parent="c_monitoring")
    v.add("c_loki", 2320, 340, 100, 55, parent="c_monitoring")
    v.add("c_tempo", 2430, 340, 100, 55, parent="c_monitoring")
    v.add("c_prom", 2540, 340, 100, 55, parent="c_monitoring")
    v.add("c_grafana", 2320, 470, 320, 120, parent="c_monitoring")
    v.add("i_grafana", 2365, 530, 230, 45, parent="c_grafana", fill=EXT_IFACE)
    v.add("c_security", 2300, 670, 360, 180, fill=CONTAINER_APP)
    v.add("c_wazuh", 2320, 715, 150, 55, parent="c_security")
    v.add("c_neuvector", 2490, 715, 150, 55, parent="c_security")
    v.add("i_security", 2365, 790, 230, 45, parent="c_security", fill=EXT_IFACE)


def _detailed_application_view_flows(v: ViewBuilder):
    """Flows of the view."""
    # flows
    v.flow("c_stacb", "c_web", "STAC requests")
    v.flow("c_staging", "c_catalog", "STAC items publication")
    v.flow("c_osam", "c_catalog", "bucket configuration")
    v.connect("Access", "c_osam", "d_bucketcfg", access="Read")
    v.flow("c_osam", "x_ovhapi", "S3 users, keys & policies")
    v.flow("c_web", "c_keycloak", "token validation, users & roles (OSAM)")
    v.flow("c_web", "c_apikey", "API key validation", bend=[(1360, 362), (1680, 362)])
    v.flow("c_apikey", "c_keycloak", "user identity")
    v.connect("Access", "c_catalog", "d_stac", access="ReadWrite")
    v.connect("Access", "c_catalog", "d_products", access="Read", bend=[(1340, 470), (1340, 1042)])
    v.connect("Access", "c_staging", "d_jobs", access="ReadWrite")
    v.connect("Access", "c_dpr", "d_jobs", access="ReadWrite")
    v.flow("c_staging", "c_dask_staging", "asset transfer tasks")
    v.flow("c_dpr", "c_dask_dpr", "processor run (eopf trigger)")
    v.flow("c_dpr", "c_daskgw", "cluster connection")
    v.flow("c_daskgw", "c_dask", "cluster creation & scaling")
    v.flow("g_csc", "c_dask_staging", "product files (HTTPS)", bend=[(145, 890)])
    v.flow("g_dataspaces", "c_dask_staging", "CDSE products (S3)", bend=[(1680, 1110), (835, 1110)])
    v.flow("g_dataspaces", "c_flows", "ADF & DEM metadata (STAC)")
    v.connect("Access", "c_dask_staging", "d_products", access="Write")
    v.connect("Access", "c_dask_dpr", "d_products", access="ReadWrite")
    v.flow(
        "c_flows",
        "c_web",
        "search, staging, catalog & processing requests (rs-client, API key)",
        bend=[(1660, 760)],
    )
    v.flow(
        "c_jupyter",
        "c_daskgw",
        "cluster management (JupyterHub token)",
        bend=[(1690, 440), (1690, 880)],
    )
    v.flow("c_jupyter", "c_prefect_server", FLOW_RUNS)
    v.flow("c_prefect_server", "c_prefect_workers", "scheduled flow runs")
    v.flow("c_prefect_workers", "c_flows", "flow-run pods")
    v.flow("c_flows", "c_prefect_server", "states, events, logs", bend=[(2030, 910), (2030, 655)])
    v.connect("Access", "c_prefect_server", "d_prefectdb", access="ReadWrite")
    v.connect("Access", "c_flows", "d_pi", access="Write")
    v.connect("Access", "c_flows", "d_quota", access="Write")
    v.connect("Access", "c_apikey", "d_apikeys", access="ReadWrite")
    v.connect("Access", "c_keycloak", "d_users", access="ReadWrite")
    v.flow("x_gitlab", "c_gitlab_runner", "CI jobs (CPM tests)")
    v.flow("c_alloy", "c_loki", "logs")
    v.flow("c_alloy", "c_tempo", "traces")
    v.flow("c_loki", "c_grafana", "")
    v.flow("c_tempo", "c_grafana", "")
    v.flow("c_prom", "c_grafana", "")

    v.note(
        "All the web UIs and APIs authenticate the users with Keycloak (OAuth2 / OIDC) or with an API key "
        "(x-api-key header), and check their Keycloak roles.",
        2300,
        900,
        360,
        70,
    )
    v.note(
        "Logs, metrics and OpenTelemetry traces of all the components are collected by Alloy and Prometheus. "
        "Wazuh and NeuVector agents run on all the nodes. Grafana also reads the PostgreSQL databases.",
        2300,
        990,
        360,
        85,
    )
    v.note(
        "Orange: external interfaces (all exposed by Envoy Gateway in HTTPS). Grey: external systems.",
        20,
        960,
        300,
        55,
    )


# =================================================================================================================
# 5. Infrastructure Logical View
# =================================================================================================================


def infrastructure_view(m: Builder):
    """View 5: Infrastructure Logical View."""
    v = m.view(
        "infrastructure",
        "5. Infrastructure Logical View",
        "Implementation and Deployment",
        "Infrastructure instances of RS-Python on OVHcloud with their software, the deployment of the "
        "application components on the node pools, and the technical flows.",
    )
    # users
    v.add("g_admin", 20, 170, 230, 230)
    v.add("dv_laptop_company", 35, 215, 200, 70, parent="g_admin", nest="Aggregation")
    v.add("dv_laptop_contractor", 35, 305, 200, 70, parent="g_admin", nest="Aggregation")
    v.add("dv_enduser", 20, 455, 230, 80)

    v.add("l_ovh", 290, 20, 2150, 1300)
    v.add("n_ovh_mgmt", 1000, 60, 440, 70, parent="l_ovh", nest="Aggregation")
    v.add("g_ops_env", 310, 160, 1710, 790, parent="l_ovh", nest="Aggregation")
    v.add("n_bastion_ops", 330, 210, 270, 210, parent="g_ops_env", nest="Aggregation", fill=CONTAINER_TECH)
    v.add("ss_ubuntu_ops", 345, 265, 240, 50, parent="n_bastion_ops", nest="Composition")
    v.add("ss_tools_ops", 345, 325, 240, 80, parent="n_bastion_ops", nest="Composition")
    v.add("n_lb_ops", 330, 455, 270, 90, parent="g_ops_env", nest="Aggregation")
    v.add("n_harbor_ops", 330, 590, 270, 130, parent="g_ops_env", nest="Aggregation", fill=CONTAINER_TECH)
    v.add("a_img_ops", 345, 650, 240, 50, parent="n_harbor_ops", nest="Assignment")
    v.add("n_nfs_ops", 330, 770, 270, 80, parent="g_ops_env", nest="Aggregation")

    v.add("n_mks_ops", 650, 200, 1350, 730, parent="g_ops_env", nest="Aggregation", fill=CONTAINER_TECH)
    v.add("n_cp_ops", 670, 250, 330, 70, parent="n_mks_ops")
    v.add("ss_k8s_ops", 1030, 250, 560, 70, parent="n_mks_ops")
    pools = [
        ("n_np_infra", ["ss_envoy", "ss_certmgr", "c_keycloak", "ss_cnpg", "c_monitoring", "c_security", "ss_velero"]),
        ("n_np_rsserver", ["c_frontend", "c_catalog", "c_prip", "c_dpr", "c_stacb", "ss_pg_rs"]),
        ("n_np_access", ["c_cadip", "c_adgs", "c_staging", "c_dask_staging"]),
        ("n_np_env", ["c_jupyter", "c_prefect", "c_daskgw", "c_apikey", "c_osam", "c_gitlab_runner", "ss_pg_env"]),
    ]
    for i, (pool, comps) in enumerate(pools):
        x = 670 + i * 330
        v.add(pool, x, 340, 315, 365, parent="n_mks_ops", fill=CONTAINER_TECH)
        for j, c in enumerate(comps):
            nest = "Realization" if c.startswith("c_") else "Composition"
            v.add(c, x + 12, 385 + j * 45, 290, 40, parent=pool, nest=nest)
    v.add("n_np_flow", 670, 725, 315, 190, parent="n_mks_ops", fill=CONTAINER_TECH)
    v.add("c_flows", 682, 790, 290, 60, parent="n_np_flow", nest="Realization")
    v.add("n_np_dpr", 1000, 725, 985, 190, parent="n_mks_ops", fill=CONTAINER_TECH)
    for i, k in enumerate(("n_np_dsched", "n_np_dworker", "n_np_bigdworker")):
        v.add(k, 1015 + i * 322, 770, 310, 60, parent="n_np_dpr")
    v.add("c_dask_dpr", 1015, 850, 954, 45, parent="n_np_dpr", nest="Realization")

    v.add("n_s3", 2050, 760, 370, 520, parent="l_ovh", nest="Aggregation", fill=CONTAINER_TECH)
    for i, a in enumerate(("a_bkt_products", "a_bkt_obs", "a_bkt_backup", "a_bkt_logs", "a_bkt_tfstate")):
        v.add(a, 2070, 830 + i * 85, 330, 65, parent="n_s3", nest="Assignment")

    v.add("g_dev_env", 310, 990, 1710, 300, parent="l_ovh", nest="Aggregation")
    v.add("n_bastion_dev", 330, 1030, 270, 90, parent="g_dev_env", nest="Aggregation")
    v.add("n_lb_dev", 330, 1160, 270, 90, parent="g_dev_env", nest="Aggregation")
    v.add("n_mks_dev", 650, 1060, 560, 160, parent="g_dev_env", nest="Aggregation")
    v.add("n_harbor_dev", 1260, 1030, 300, 80, parent="g_dev_env", nest="Aggregation")
    v.add("n_nfs_dev", 1260, 1160, 300, 80, parent="g_dev_env", nest="Aggregation")

    ext = [
        ("n_csc", "HTTPS 443 (OData, downloads)"),
        ("n_dataspaces", "HTTPS 443 (STAC, S3)"),
        ("n_ghcr", "HTTPS 443 (public images)"),
        ("n_letsencrypt", "HTTPS 443 (ACME)"),
        ("n_eopf_gitlab", "HTTPS 443 (CI jobs)"),
    ]
    for i, (k, label) in enumerate(ext):
        v.add(k, 2480, 200 + i * 100, 250, 70, fill=EXTERNAL)
        v.flow("n_mks_ops", k, label)
    _infrastructure_view_flows(v)


def _infrastructure_view_flows(v: ViewBuilder):
    """Flows of the view."""
    # flows
    v.flow("g_admin", "n_bastion_ops", "SSH 22/tcp (whitelisted IPs)")
    v.flow("g_admin", "n_bastion_dev", "SSH 22/tcp (whitelisted IPs)", bend=[(270, 300), (270, 1075)])
    v.flow("g_admin", "n_ovh_mgmt", "HTTPS 443 + 2FA (Control Panel)", bend=[(135, 80)])
    v.flow("dv_enduser", "n_lb_ops", "HTTPS 443 (*.<domain>)")
    v.flow("dv_enduser", "n_s3", "HTTPS 443 (S3 API, pre-signed URLs)", bend=[(135, 1340), (2235, 1340)])
    v.flow("n_bastion_ops", "n_cp_ops", "HTTPS 6443 (kubectl, Helm)")
    v.flow("n_bastion_ops", "n_ovh_mgmt", "HTTPS 443 (Terraform)", bend=[(465, 115)])
    v.flow("n_lb_ops", "n_np_infra", "HTTPS 443 (Envoy Gateway)")
    v.flow("n_mks_ops", "n_harbor_ops", "HTTPS 443 (private images)")
    v.flow("n_mks_ops", "n_nfs_ops", NFS)
    v.flow("n_mks_ops", "n_ovh_mgmt", "HTTPS 443 (OVHcloud API)")
    v.flow("n_mks_ops", "n_s3", "HTTPS 443 (S3 API)")
    v.flow("n_bastion_dev", "n_mks_dev", "HTTPS 6443")
    v.flow("n_lb_dev", "n_mks_dev", HTTPS_443)
    v.flow("n_mks_dev", "n_harbor_dev", HTTPS_443)
    v.flow("n_mks_dev", "n_nfs_dev", "NFS")
    v.flow("n_mks_dev", "n_s3", "HTTPS 443 (S3 API)", bend=[(930, 1270), (1990, 1270)])
    v.note(
        "The dev cluster has the same node pools, software and deployment as the ops cluster, with a smaller "
        "sizing. Intra-cluster flows (Envoy Gateway to the services, services to databases and Dask) use the "
        "Kubernetes pod network.",
        1600,
        1030,
        400,
        90,
        parent="g_dev_env",
    )


# =================================================================================================================
# 6. Network View
# =================================================================================================================


def network_view(m: Builder):
    """View 6: Network View."""
    v = m.view(
        "network",
        "6. Network View",
        "Technology",
        "Network zones (groupings), networks, nodes and network flows (protocols, ports, filtering) of the "
        "RS-Python platform on OVHcloud.",
    )
    # Internet zone
    v.add("g_inet", 10, 10, 1970, 330)
    v.add("g_admin", 25, 45, 650, 205, parent="g_inet", nest="Aggregation")
    for loc, dev, x in (("l_company", "dv_laptop_company", 40), ("l_contractor", "dv_laptop_contractor", 360)):
        v.add(loc, x, 80, 300, 155, parent="g_admin", nest="Aggregation")
        v.add(dev, x + 15, 125, 270, 85, parent=loc, nest="Aggregation")
    v.add("l_users", 700, 80, 300, 155, parent="g_inet", nest="Aggregation")
    v.add("dv_enduser", 715, 125, 270, 85, parent="l_users", nest="Aggregation")
    v.add("g_ext", 1030, 45, 935, 205, parent="g_inet", nest="Aggregation", fill=EXTERNAL)
    for i, k in enumerate(("n_csc", "n_dataspaces", "n_ghcr", "n_letsencrypt", "n_eopf_gitlab", "n_dns")):
        v.add(k, 1045 + (i % 3) * 307, 85 + (i // 3) * 80, 295, 65, parent="g_ext", nest="Aggregation", fill=EXTERNAL)
    v.add("nw_internet", 25, 275, 1940, 40, parent="g_inet", nest="Aggregation")

    # OVHcloud
    v.add("l_ovh", 10, 375, 1970, 905)
    v.add("n_ovh_mgmt", 240, 425, 230, 85, parent="l_ovh", nest="Aggregation")
    v.add("n_s3", 520, 425, 230, 85, parent="l_ovh", nest="Aggregation")
    v.add("n_harbor_ops", 1190, 425, 240, 85, parent="l_ovh", nest="Aggregation")
    v.add("n_harbor_dev", 1460, 425, 240, 85, parent="l_ovh", nest="Aggregation")
    for env, x0 in (("ops", 30), ("dev", 1000)):
        g = f"g_{env}_env"
        v.add(g, x0, 545, 950, 715, parent="l_ovh", nest="Aggregation")
        pub, priv = f"g_pub_{env}", f"g_priv_{env}"
        v.add(pub, x0 + 15, 580, 920, 145, parent=g, nest="Aggregation")
        v.add(f"n_bastion_{env}", x0 + 30, 625, 270, 85, parent=pub, nest="Aggregation")
        v.add(f"n_lb_{env}", x0 + 330, 625, 270, 85, parent=pub, nest="Aggregation")
        v.add(f"n_router_{env}", x0 + 630, 625, 270, 85, parent=pub, nest="Aggregation")
        v.add(priv, x0 + 15, 750, 920, 495, parent=g, nest="Aggregation")
        v.add(f"nw_priv_{env}", x0 + 660, 790, 250, 55, parent=priv, nest="Aggregation")
        v.add(
            f"n_mks_{env}",
            x0 + 30,
            880,
            590,
            210 if env == "ops" else 150,
            parent=priv,
            nest="Aggregation",
            fill=CONTAINER_TECH if env == "ops" else None,
        )
        v.add(f"n_nfs_{env}", x0 + 660, 880, 250, 90, parent=priv, nest="Aggregation")
        v.connect("Association", f"n_router_{env}", f"nw_priv_{env}")
        v.connect("Association", f"n_mks_{env}", f"nw_priv_{env}")
        v.connect("Association", f"n_nfs_{env}", f"nw_priv_{env}")
    v.add("n_cp_ops", 50, 935, 270, 90, parent="n_mks_ops")
    v.add("n_workers_ops", 340, 935, 260, 90, parent="n_mks_ops")
    v.note(
        "Filtering (OpenStack security groups and MKS IP restrictions):\n"
        "- bastion: SSH 22/tcp from the company and contractor IP addresses only\n"
        "- load balancer: HTTPS 443 from the Internet\n"
        "- Kubernetes API: 6443/tcp from the bastion IP address only\n"
        "Managed services (object storage, registries, OVHcloud APIs) expose authenticated public HTTPS "
        "endpoints, reached by the cluster nodes through the router.",
        45,
        1105,
        575,
        125,
        parent="g_priv_ops",
    )
    v.note(
        "Same network design and filtering as the production environment. Administration through the dev "
        "bastion only.",
        1015,
        1110,
        575,
        60,
        parent="g_priv_dev",
    )

    # flows
    v.flow("g_admin", "n_bastion_ops", "SSH 22/tcp", bend=[(165, 355)])
    v.flow("g_admin", "n_ovh_mgmt", "HTTPS 443 + 2FA (web console)", bend=[(355, 360)])
    v.flow("g_admin", "n_bastion_dev", "SSH 22/tcp", bend=[(600, 355), (1165, 355)])
    v.flow("dv_enduser", "n_lb_ops", "HTTPS 443 (*.<domain>)", bend=[(495, 362)])
    v.flow("dv_enduser", "n_s3", "HTTPS 443 (S3 API, pre-signed URLs)")
    v.flow("n_bastion_ops", "n_cp_ops", "HTTPS 6443 (kubectl, Helm)")
    v.flow("n_bastion_ops", "n_ovh_mgmt", "HTTPS 443 (Terraform, APIs)")
    v.flow("n_lb_ops", "n_workers_ops", "HTTPS 443 (Envoy Gateway)")
    v.flow("n_workers_ops", "n_nfs_ops", NFS)
    v.flow("n_router_ops", "nw_internet", "HTTPS 443 outbound (SNAT)", bend=[(795, 345)])
    v.flow("n_bastion_dev", "n_mks_dev", "HTTPS 6443")
    v.flow("n_lb_dev", "n_mks_dev", HTTPS_443)
    v.flow("n_mks_dev", "n_nfs_dev", NFS)
    v.flow("n_router_dev", "nw_internet", "HTTPS 443 outbound (SNAT)", bend=[(1765, 345)])
