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

"""RS-Python architecture model: elements and functional packages."""

from typing import NamedTuple

from model_builder import Builder

# =================================================================================================================
# Elements
# =================================================================================================================


class Package(NamedTuple):
    """Functional package: application function with its functions."""

    key: str
    name: str
    description: str
    functions: list[tuple[str, str]]
    services: list[str]
    components: str


FUNCTIONAL_PACKAGES = [
    Package(
        "fp_ext",
        "FP1 - External Data Access",
        (
            "Search, in read-only mode, the data of the Copernicus ground segment and of the data spaces. rs-server "
            "translates the STAC API requests into OData requests to the stations, and the OData responses into STAC "
            "items."
        ),
        [
            (
                "Search CADIP raw data sessions",
                "STAC API on the CADIP acquisition stations: sessions as items, files as assets.",
            ),
            (
                "Search auxiliary data (AUXIP)",
                "STAC API on the AUXIP / ADGS instances: one item per auxiliary data file.",
            ),
            (
                "Search production products (PRIP)",
                "STAC API on the PRIP instances: Level-0, Level-1 and Level-2 products.",
            ),
            (
                "STAC / OData mapping",
                "Translation of the requests, virtual collections, product type mapping to EOPF types.",
            ),
            (
                "Search CDSE and EarthDataHub",
                "Direct STAC search of the CDSE and DestinE EarthDataHub by the client library.",
            ),
        ],
        ["s_search"],
        (
            "rs-server-cadip, rs-server-adgs, rs-server-prip, rs-client-libraries (CdseClient, EarthDataHubClient), "
            "STAC browsers (CADIP, AUXIP, PRIP)"
        ),
    ),
    Package(
        "fp_staging",
        "FP2 - Data Staging",
        (
            "Copy products from the external data sources into the RS-Python object storage, and publish their STAC "
            "items in the catalog (OGC API - Processes service, run on a Dask cluster)."
        ),
        [
            ("Staging job management", "OGC API - Processes: start, follow, dismiss staging jobs."),
            (
                "Parallel asset transfer",
                "Download of the assets from the stations (HTTPS) or the CDSE (S3) on the staging Dask cluster.",
            ),
            ("Write to object storage", "Store the assets in the bucket given by the bucket configuration."),
            (
                "Catalog publication",
                "Publish the STAC items, with assets referencing the object storage, in a catalog collection.",
            ),
        ],
        ["s_staging"],
        "rs-server-staging, staging Dask cluster, Dask Gateway, staging flows (rs-workflows)",
    ),
    Package(
        "fp_catalog",
        "FP3 - Catalog & Data Management",
        (
            "STAC catalog of the products managed by RS-Python (raw data, auxiliary data, Level-0 to Level-2 "
            "products), stored in PostgreSQL / pgstac, with ownership, fine access rights and data lifecycle."
        ),
        [
            (
                "Collections & items management",
                "Create, read, update, delete collections and items (STAC API transactions).",
            ),
            ("Spatio-temporal search", "STAC API search with spatial, temporal and CQL2 metadata filters."),
            (
                "Ownership & access control",
                "Collections owned by users; rs_catalog_<owner>:<collection>_<right> roles.",
            ),
            ("Asset download", "Redirection to temporary pre-signed URLs of the object storage."),
            ("Data lifecycle", "Timestamps and expiration of the items according to the bucket configuration."),
            ("OData PRIP interface", "Exposure of the catalog products with the OData interface of the ESA PRIP."),
        ],
        ["s_catalog", "s_access"],
        "rs-server-catalog, pgstac database (CloudNativePG), STAC browser (catalog), object storage",
    ),
    Package(
        "fp_osam",
        "FP4 - Object Storage Access Management",
        (
            "Keep the object storage accounts and access policies of the users consistent with their catalog rights, "
            "and deliver their personal S3 credentials."
        ),
        [
            (
                "S3 accounts synchronisation",
                "Create / delete the object storage accounts according to the Keycloak accounts.",
            ),
            (
                "Access policy computation",
                "Compute and apply the bucket/folder access policies from the catalog roles.",
            ),
            ("S3 credentials delivery", "Return the personal S3 credentials of the user."),
            (
                "Bucket configuration",
                "Serve the bucket configuration (owner, collection, product type, expiration, bucket).",
            ),
        ],
        ["s_access"],
        "rs-server-osam, OVHcloud API, OVHcloud Object Storage, OSAM operation flows",
    ),
    Package(
        "fp_processing",
        "FP5 - Product Processing",
        (
            "Run the EOPF DPR processors (Sentinel-1, -2, -3) and the SAFE to Zarr conversion on Dask clusters, "
            "through an OGC API - Processes service."
        ),
        [
            ("Task table & payload generation", "Retrieve the task tables and compute the EOPF payload files."),
            (
                "Processor execution on Dask",
                "Trigger the processor (eopf trigger) on the Dask cluster of the processor.",
            ),
            (
                "Job monitoring & cancellation",
                "Status, progress, log streaming and cancellation of the processing jobs.",
            ),
            ("SAFE / Zarr conversion", "Conversion of the legacy SAFE products and auxiliary files to Zarr."),
            ("Quicklook generation", "Generation of the quicklooks of the Sentinel-3 OLCI products."),
        ],
        ["s_processing"],
        "rs-dpr-service, DPR Dask clusters (EOPF CPM and processors), Dask Gateway, processing flows",
    ),
    Package(
        "fp_orchestration",
        "FP6 - Workflow Orchestration",
        "Implement, schedule, chain and monitor the processing chains as Prefect flows, on demand or systematically.",
        [
            ("On-demand flows", "Search, staging, processing and conversion flows started by the users."),
            ("Systematic processing", "Flows chained by Prefect automations on the events of new products."),
            ("Scheduling & work pools", "Schedules, work pools (integrated, sandbox, monitoring), concurrency limits."),
            ("Custom flow development", "Users' own flows, written with the rs-client-libraries."),
            ("Performance indicators", "Completeness and timeliness of the production (PI database)."),
        ],
        ["s_orchestration"],
        "Prefect server and workers, rs-workflows flows, rs-workflow-deployment, PI database",
    ),
    Package(
        "fp_venv",
        "FP7 - Virtual Environment & User Interfaces",
        "Per-group workspace and user interfaces to discover the data, call the services and develop the processing.",
        [
            ("Interactive notebooks", "JupyterHub sessions with the RS-Python libraries pre-installed."),
            ("Dask cluster management", "Creation and scaling of the Dask clusters through Dask Gateway."),
            ("Client libraries", "rs-client-libraries: Python access to all the RS-Python services."),
            ("API documentation", "Aggregated Swagger page of all the web services."),
            ("Product browsing", "STAC browsers of the catalog and of the stations."),
        ],
        ["s_venv"],
        "JupyterHub, Dask Gateway, rs-client-libraries, rs-server-frontend, STAC browsers",
    ),
    Package(
        "fp_iam",
        "FP8 - Identity & Access Management",
        "Authenticate the users and the processing, and authorise each request according to the Keycloak roles.",
        [
            ("User authentication", "OAuth2 / OpenID Connect login with Keycloak."),
            ("API key management", "Creation, renewal and revocation of long-lived API keys."),
            ("Request authorisation", "Check of the Keycloak roles for each request of each service."),
            ("User & role administration", "Management of the accounts, groups and roles in Keycloak."),
        ],
        ["s_admin"],
        "Keycloak, API Key Manager, rs-server authentication (all services), Envoy Gateway",
    ),
    Package(
        "fp_ops",
        "FP9 - Platform Operations & Monitoring",
        "Deploy, monitor, secure and back up the platform.",
        [
            (
                "Logs, metrics & traces",
                "OpenTelemetry instrumentation, collection by Alloy and Prometheus, storage in Loki and Tempo.",
            ),
            ("Dashboards & alerting", "Grafana dashboards, exploration and alerts."),
            ("Object storage quota monitoring", "Access logs of the buckets loaded into the quota database."),
            ("Security monitoring", "Intrusion detection (Wazuh) and container security (NeuVector)."),
            ("Backup & restore", "Velero backups of Kubernetes resources and volumes, CloudNativePG database backups."),
            (
                "Infrastructure as code deployment",
                "Terraform and Ansible deployment of the cluster and of all the applications.",
            ),
        ],
        ["s_admin"],
        (
            "Grafana, Prometheus, Loki, Tempo, Alloy, Wazuh, NeuVector, Velero, CloudNativePG, rs-infra-core "
            "playbooks, bastion"
        ),
    ),
]


def elements(m: Builder):
    """All the elements of the model."""
    _business(m)
    _application_services_of_the_system_of_interest(m)
    _system_of_interest_and_its_components(m)
    _interfaces(m)
    _data_objects(m)
    _external_application_components(m)
    _technology_services_context(m)
    _technology_ovhcloud(m)
    _technology_outside_ovhcloud(m)
    _functional_packages(m)


def _business(m: Builder):
    """Elements: business."""
    el = m.el
    el(
        "r_user",
        "BusinessRole",
        "End User",
        "Data operator or analyst: searches, stages and processes Sentinel products by running the existing flows, "
        "then views and downloads the generated products.",
    )
    el(
        "r_dev",
        "BusinessRole",
        "Flow Developer",
        "Processing chain developer or IVV engineer: customises the processing, writes custom Prefect flows and "
        "integrates new processors.",
    )
    el(
        "r_op",
        "BusinessRole",
        "Operator",
        "Monitors the platform and the production (flows, processing, performance indicators) with a subset of the "
        "administration tools.",
    )
    el(
        "r_admin",
        "BusinessRole",
        "Administrator",
        "Deploys and maintains the platform, manages the user accounts and rights, initialises the processing "
        "environment and supports the users.",
    )
    el(
        "r_sec",
        "BusinessRole",
        "Security Officer",
        "Supervises the security of the platform: intrusion detection, vulnerabilities, container security.",
    )
    el(
        "a_eopf",
        "BusinessActor",
        "EOPF project (ESA)",
        "Earth Observation Processing Framework project: develops the re-engineered DPR processors and the CPM.",
    )
    el(
        "e_sentinel",
        "Equipment",
        "Sentinel-1/-2/-3 satellites",
        "Copernicus Sentinel satellites, whose raw data is downlinked to the acquisition ground stations.",
    )


def _application_services_of_the_system_of_interest(m: Builder):
    """Elements: application services of the system of interest."""
    el = m.el
    el(
        "s_search",
        "ApplicationService",
        "External Data Search",
        "Search the raw data sessions (CADIP), auxiliary data (AUXIP) and products (PRIP) of the Copernicus ground "
        "segment with the STAC API.",
    )
    el(
        "s_staging",
        "ApplicationService",
        "Data Staging",
        "Copy products from the external data sources into the RS-Python object storage and catalog (OGC API - "
        "Processes).",
    )
    el(
        "s_catalog",
        "ApplicationService",
        "Product Catalog",
        "Search, read and manage the products with the STAC API (and the OData PRIP interface).",
    )
    el(
        "s_access",
        "ApplicationService",
        "Product Download & Storage Access",
        "Personal S3 credentials (OSAM), direct access to the buckets and download of the assets with pre-signed URLs.",
    )
    el(
        "s_processing",
        "ApplicationService",
        "Product Processing",
        "Run the DPR processors and the conversions on Dask clusters (OGC API - Processes).",
    )
    el(
        "s_orchestration",
        "ApplicationService",
        "Workflow Orchestration",
        "Run, schedule, chain and monitor the processing flows (Prefect), on demand or systematically.",
    )
    el(
        "s_venv",
        "ApplicationService",
        "Virtual Environment",
        "JupyterHub workspace with the client libraries, Dask clusters, Swagger page and STAC browsers.",
    )
    el(
        "s_admin",
        "ApplicationService",
        "Platform Administration & Monitoring",
        "User accounts and rights, API keys, monitoring dashboards, security monitoring, backups.",
    )


def _system_of_interest_and_its_components(m: Builder):
    """Elements: system of interest and its components."""
    el = m.el
    el(
        "c_soi",
        "ApplicationComponent",
        "RS-Python (Copernicus Reference System Python)",
        "System of Interest: open-source software solution to implement, deploy, operate and monitor Copernicus "
        "Sentinel data processing workflows based on the EOPF processors. Deployed on OVHcloud.",
    )
    el(
        "c_web",
        "ApplicationComponent",
        "RS-Python Web Services (rs-server, rs-dpr-service)",
        "Web services exposed behind the single domain rspy.<domain>, protected by authentication and fine-grained "
        "authorisation, documented in a single Swagger page.",
        repository="rs-server, rs-dpr-service, rs-helm",
    )
    el(
        "c_frontend",
        "ApplicationComponent",
        "rs-server-frontend",
        "Serves the aggregated Swagger page / OpenAPI specification of all the services (built at CI time).",
        image="ghcr.io/rs-python/rs-server-frontend",
    )
    el(
        "c_cadip",
        "ApplicationComponent",
        "rs-server-cadip",
        "STAC API on the CADIP acquisition stations (raw data sessions), translated into OData requests.",
        image="ghcr.io/rs-python/rs-server-cadip",
    )
    el(
        "c_adgs",
        "ApplicationComponent",
        "rs-server-adgs (AUXIP)",
        "STAC API on the AUXIP / ADGS instances (auxiliary data files).",
        image="ghcr.io/rs-python/rs-server-adgs",
    )
    el(
        "c_prip",
        "ApplicationComponent",
        "rs-server-prip",
        "STAC API on the PRIP instances (Level-0, Level-1 and Level-2 products).",
        image="ghcr.io/rs-python/rs-server-prip",
    )
    el(
        "c_catalog",
        "ApplicationComponent",
        "rs-server-catalog",
        "STAC API of the RS-Python catalog (stac-fastapi-pgstac) with ownership, authorisation, asset checks, "
        "download with pre-signed URLs, lifecycle and OData PRIP interface.",
        image="ghcr.io/rs-python/rs-server-catalog",
    )
    el(
        "c_staging",
        "ApplicationComponent",
        "rs-server-staging",
        "OGC API - Processes service (pygeoapi) with the 'staging' process, run on the staging Dask cluster.",
        image="ghcr.io/rs-python/rs-server-staging",
    )
    el(
        "c_osam",
        "ApplicationComponent",
        "rs-server-osam",
        "Object Storage Access Manager: synchronises the S3 accounts and access policies with the Keycloak roles and "
        "delivers the personal S3 credentials.",
        image="ghcr.io/rs-python/rs-server-osam",
    )
    el(
        "c_dpr",
        "ApplicationComponent",
        "rs-dpr-service",
        "OGC API - Processes service (pygeoapi) that runs the DPR processors on their Dask clusters, one image per "
        "Python and Dask version.",
        image="ghcr.io/rs-python/rs-dpr-service_py<python>-<dask>",
    )
    el(
        "c_stacb",
        "ApplicationComponent",
        "STAC Browsers (catalog, CADIP, AUXIP, PRIP)",
        "Radiant Earth STAC Browser web interfaces of the catalog and of the stations.",
    )
    el(
        "c_prefect",
        "ApplicationComponent",
        "Prefect Orchestrator",
        "Prefect 3 server (API, UI, automations) and Kubernetes workers of the integrated, sandbox and monitoring "
        "work pools.",
    )
    el(
        "c_prefect_server",
        "ApplicationComponent",
        "Prefect Server (API, UI, automations)",
        "Prefect 3 server, with its PostgreSQL database, protected by Keycloak.",
    )
    el(
        "c_prefect_workers",
        "ApplicationComponent",
        "Prefect Workers (integrated, sandbox, monitoring)",
        "Prefect Kubernetes workers: start the flow runs as Kubernetes jobs.",
    )
    el(
        "c_flows",
        "ApplicationComponent",
        "Processing Flows (rs-workflows, rs-client-libraries)",
        "Prefect flows (search, staging, processing, conversion, operation) deployed by rs-workflow-deployment, "
        "calling the services with the rs-client-libraries and an API key.",
        repository="rs-client-libraries, rs-workflow-deployment",
    )
    el(
        "c_jupyter",
        "ApplicationComponent",
        "JupyterHub",
        "One JupyterLab session per user, with the RS-Python libraries and one kernel per Dask version.",
    )
    el(
        "c_daskgw",
        "ApplicationComponent",
        "Dask Gateway",
        "Creates and scales the Dask clusters, with the JupyterHub authentication.",
    )
    el(
        "c_dask",
        "ApplicationComponent",
        "Dask Clusters",
        "Dask schedulers and workers running the staging tasks and the DPR processors.",
    )
    el(
        "c_dask_staging",
        "ApplicationComponent",
        "Staging Dask Cluster",
        "Dask cluster of the staging service: parallel download of the assets into the object storage.",
        image="ghcr.io/rs-python/dask/staging/k8s",
    )
    el(
        "c_dask_dpr",
        "ApplicationComponent",
        "DPR Dask Clusters (EOPF CPM and DPR processors)",
        "One Dask cluster per processor: S1 L0, S3 L0, S1 ARD, S3 L1/L2 OLCI, SAFE to Zarr conversion, mockup.",
        image="dask/<processor>/k8s",
    )
    el(
        "c_keycloak",
        "ApplicationComponent",
        "Keycloak (IAM)",
        "Identity and access management: user accounts, groups, roles, OAuth2 / OpenID Connect.",
    )
    el(
        "c_apikey",
        "ApplicationComponent",
        "API Key Manager",
        "Creates, renews and revokes the API keys that carry the identity and rights of the users "
        "(csgroup-oss/apikey-manager).",
    )
    el(
        "c_monitoring",
        "ApplicationComponent",
        "Monitoring Stack (Grafana, Prometheus, Loki, Tempo, Alloy)",
        "Observability of the platform: logs, metrics, traces, dashboards and alerts.",
        repository="rs-infra-monitoring",
    )
    el("c_alloy", "ApplicationComponent", "Grafana Alloy", "Collects the logs and the OpenTelemetry traces.")
    el("c_loki", "ApplicationComponent", "Loki", "Logs of all the pods.")
    el("c_tempo", "ApplicationComponent", "Tempo", "Traces, from the Prefect flows to the services and Dask workers.")
    el("c_prom", "ApplicationComponent", "Prometheus", "Metrics of the cluster, nodes and pods.")
    el("c_grafana", "ApplicationComponent", "Grafana", "Dashboards, exploration of logs, metrics, traces, alerts.")
    el(
        "c_security",
        "ApplicationComponent",
        "Security Monitoring (Wazuh, NeuVector)",
        "Intrusion detection and container security, deployed from a non-public repository.",
    )
    el("c_wazuh", "ApplicationComponent", "Wazuh", "Intrusion detection, security events, vulnerability detection.")
    el("c_neuvector", "ApplicationComponent", "NeuVector", "Container and Kubernetes runtime security.")
    el(
        "c_gitlab_runner",
        "ApplicationComponent",
        "GitLab Runner (EOPF CPM CI)",
        "GitLab runner that runs the EOPF CPM tests on the cluster.",
    )


def _interfaces(m: Builder):
    """Elements: interfaces."""
    el = m.el
    el(
        "i_web",
        "ApplicationInterface",
        "RS-Python Web API & Swagger (rspy.<domain>)",
        "HTTPS REST API: STAC API (/cadip, /auxip, /prip, /catalog), OGC API - Processes (/processes, /dpr), OData, "
        "/storage, /auth, Swagger (/docs). OAuth2 cookie or x-api-key header.",
    )
    el("i_docs", "ApplicationInterface", "/docs, /openapi.json (Swagger UI)")
    el("i_cadip", "ApplicationInterface", "/cadip (STAC API)")
    el("i_auxip", "ApplicationInterface", "/auxip (STAC API)")
    el("i_prip", "ApplicationInterface", "/prip (STAC API)")
    el("i_catalog", "ApplicationInterface", "/catalog (STAC API, OData)")
    el("i_staging", "ApplicationInterface", "/processes, /jobs (OGC API-P)")
    el("i_osam", "ApplicationInterface", "/storage (S3 credentials)")
    el("i_dpr", "ApplicationInterface", "/dpr (OGC API - Processes)")
    el("i_stacb", "ApplicationInterface", "STAC Browser UIs (stac-browser-*.<domain>)")
    el("i_jupyter", "ApplicationInterface", "JupyterLab UI (processing.<domain>/jupyter)")
    el("i_prefect", "ApplicationInterface", "Prefect UI & API (processing.<domain>/dashboard)")
    el("i_dask", "ApplicationInterface", "Dask dashboards (dash-dask.processing.<domain>)")
    el("i_apikey", "ApplicationInterface", "API Key Manager API (apikeymanager.<domain>)")
    el("i_keycloak", "ApplicationInterface", "Keycloak login & admin console (iam.<domain>)")
    el("i_grafana", "ApplicationInterface", "Grafana UI (monitoring.<domain>)")
    el("i_security", "ApplicationInterface", "Security consoles (Wazuh, NeuVector)")


def _data_objects(m: Builder):
    """Elements: data objects."""
    el = m.el
    el(
        "d_products",
        "DataObject",
        "Products & Auxiliary Data Files (S3 buckets)",
        "Raw data (CADU), auxiliary data files, Level-0 to Level-2 products (Zarr, SAFE), payloads, reports, "
        "quicklooks, stored under <bucket>/<owner>/<collection>/.",
    )
    el("d_stac", "DataObject", "STAC Collections & Items (pgstac)")
    el("d_jobs", "DataObject", "Staging & Processing Jobs")
    el("d_pi", "DataObject", "Performance Indicators")
    el("d_quota", "DataObject", "S3 Access Logs & Quotas")
    el("d_prefectdb", "DataObject", "Flow Runs, Deployments & Events")
    el("d_apikeys", "DataObject", "API Keys")
    el("d_users", "DataObject", "Users, Groups & Roles")
    el(
        "d_bucketcfg",
        "DataObject",
        "Bucket Configuration",
        "CSV table owner, collection, product type, expiration delay, bucket.",
    )


def _external_application_components(m: Builder):
    """Elements: external application components."""
    el = m.el
    el(
        "x_cadip",
        "ApplicationComponent",
        "CADIP Stations",
        "CADU Interface delivery Points of the Copernicus acquisition ground stations: raw data sessions (OData API).",
    )
    el(
        "x_auxip",
        "ApplicationComponent",
        "AUXIP (ADGS)",
        "Auxiliary Data Gathering Service: auxiliary data files (OData API).",
    )
    el(
        "x_prip",
        "ApplicationComponent",
        "PRIP (Production Services)",
        "Production service Interface delivery Points: Level-0, Level-1 and Level-2 products (OData API).",
    )
    el(
        "x_cdse",
        "ApplicationComponent",
        "Copernicus Data Space Ecosystem (CDSE)",
        "Public STAC API and S3 object storage of the Copernicus Data Space Ecosystem.",
    )
    el(
        "x_edh",
        "ApplicationComponent",
        "DestinE EarthDataHub",
        "Destination Earth data lake: public STAC API, e.g. Copernicus Digital Elevation Model.",
    )
    el(
        "x_ovhapi",
        "ApplicationComponent",
        "OVHcloud API",
        "API of the cloud provider, used by OSAM to manage the object storage users, keys and access policies.",
    )
    el(
        "x_github",
        "ApplicationComponent",
        "GitHub (code, CI, GHCR, Helm repository, PyPI publication)",
        "Source code, CI/CD (GitHub Actions), public Docker images (ghcr.io/rs-python), Helm charts, documentation.",
    )
    el(
        "x_gitlab",
        "ApplicationComponent",
        "EOPF CPM GitLab",
        "gitlab.eopf.copernicus.eu: EOPF CPM and DPR processors source code and CI.",
    )
    el("g_csc", "Grouping", "Copernicus Ground Segment")
    el("g_dataspaces", "Grouping", "Data Spaces")
    el("g_supply", "Grouping", "Software Supply Chain")
    el("g_ovh", "Grouping", "OVHcloud Public Cloud (hosting provider)")


def _technology_services_context(m: Builder):
    """Elements: technology services (context)."""
    el = m.el
    el("ts_mks", "TechnologyService", "Managed Kubernetes Service (MKS)")
    el("ts_s3", "TechnologyService", "Object Storage (S3)")
    el("ts_registry", "TechnologyService", "Managed Private Registry (Harbor)")
    el("ts_iaas", "TechnologyService", "Compute & Network (VMs, load balancers, private networks, NFS)")


def _technology_ovhcloud(m: Builder):
    """Elements: technology: ovhcloud."""
    el = m.el
    el("l_ovh", "Location", "OVHcloud - Public Cloud project, region GRA (Gravelines, France)")
    el("g_ops_env", "Grouping", "Production environment (ops)")
    el("g_dev_env", "Grouping", "Development environment (dev)")
    el(
        "n_ovh_mgmt",
        "Node",
        "OVHcloud Control Panel (web + 2FA) & APIs (OVHcloud, OpenStack)",
        "Management plane of the cloud provider, operated by OVHcloud.",
    )
    for env, envname in (("ops", "ops"), ("dev", "dev")):
        el(
            f"n_bastion_{env}",
            "Node",
            f"Bastion VM ({envname}) - b3-8, public IP",
            "OpenStack instance on Ext-Net; security group: SSH 22/tcp from the whitelisted IP addresses only "
            "(company and contractor sites).",
            flavor="b3-8",
            os="Ubuntu 24.04 LTS",
        )
        el(
            f"n_lb_{env}",
            "Node",
            f"Load Balancer ({envname}) - public IP, HTTPS 443",
            "OVHcloud Public Cloud Load Balancer created by Kubernetes for the Envoy Gateway service: single entry "
            "point of all the web services.",
        )
        el(
            f"n_mks_{env}",
            "Node",
            f"Managed Kubernetes Cluster ({envname}) - OVHcloud MKS",
            "Managed Kubernetes cluster on the private network, Kubernetes API restricted to the bastion IP address.",
        )
        el(
            f"n_harbor_{env}",
            "Node",
            f"Managed Private Registry ({envname}) - Harbor",
            "OVHcloud managed Harbor registry: private images that must never be public, proxy cache of the public "
            "registries.",
        )
        el(
            f"n_nfs_{env}",
            "Node",
            f"Shared File System ({envname}) - Manila NFS",
            "OpenStack Manila NFS shares for the ReadWriteMany volumes.",
        )
        el(
            f"n_router_{env}",
            "Node",
            f"Router ({envname}) - outgoing traffic (SNAT)",
            "Router of the private network: gives the outgoing Internet access to the cluster nodes.",
        )
        el(f"nw_priv_{env}", "CommunicationNetwork", f"Private network ({envname}) - 192.168.1.0/24 subnet")
    el("ss_ubuntu_ops", "SystemSoftware", "Ubuntu 24.04 LTS")
    el("ss_tools_ops", "SystemSoftware", "Ansible, Terraform, OpenStack CLI, kubectl, Helm, Kustomize")
    el("n_cp_ops", "Node", "Kubernetes control plane (managed by OVHcloud) - API 6443 restricted to the bastion IP")
    el("n_workers_ops", "Node", "Worker nodes (8 node pools, autoscaled)")
    el("ss_k8s_ops", "SystemSoftware", "Worker node software: OVHcloud MKS node image (Linux), kubelet, containerd")
    pools = [
        ("n_np_infra", "Node pool infra - b3-16, 2 to 10 nodes", "b3-16", "infra"),
        ("n_np_rsserver", "Node pool rs_server - b3-16, up to 3 nodes", "b3-16", "rs_server"),
        ("n_np_access", "Node pool access_csc - b3-8", "b3-8", "access_csc"),
        ("n_np_env", "Node pool rs_env - b3-16, up to 3 nodes", "b3-16", "rs_env"),
        ("n_np_flow", "Node pool prefect_flow - b3-16, 0 to 5 nodes", "b3-16", "prefect_flow"),
        ("n_np_dsched", "dask_scheduler - r3-64, up to 1 node", "r3-64", "dask_scheduler"),
        ("n_np_dworker", "dask_worker_on_demand - r3-64", "r3-64", "dask_worker_on_demand"),
        ("n_np_bigdworker", "big_dask_worker_on_demand - r3-128", "r3-128", "big_dask_worker_on_demand"),
    ]
    for key, name, flavor, label in pools:
        el(key, "Node", name, f"Pods scheduled with the node-role.kubernetes.io/{label} label.", flavor=flavor)
    el("n_np_dpr", "Node", "DPR processing node pools (autoscaled from 0)")
    el("ss_envoy", "SystemSoftware", "Envoy Gateway (Gateway API)")
    el("ss_certmgr", "SystemSoftware", "cert-manager (Let's Encrypt)")
    el("ss_cnpg", "SystemSoftware", "CloudNativePG operator, Keycloak PostgreSQL")
    el("ss_velero", "SystemSoftware", "Velero (backups)")
    el("ss_pg_rs", "SystemSoftware", "PostgreSQL (CNPG): pgstac, jobs, PI, quotas")
    el("ss_pg_env", "SystemSoftware", "PostgreSQL (CNPG): Prefect, API keys")
    el(
        "n_s3",
        "Node",
        "OVHcloud Object Storage (S3, region GRA) - public HTTPS endpoint",
        "S3-compatible object storage of the project, shared by the two environments (buckets prefixed by the "
        "cluster name).",
    )
    el("a_bkt_products", "Artifact", "Product buckets (one per retention period)")
    el("a_bkt_obs", "Artifact", "Monitoring buckets (Loki logs, Tempo traces)")
    el("a_bkt_backup", "Artifact", "Backup buckets (PostgreSQL, Velero)")
    el("a_bkt_logs", "Artifact", "Access logs bucket")
    el("a_bkt_tfstate", "Artifact", "Terraform state bucket")
    el("a_img_ops", "Artifact", "Private container images (ops)")
    el("a_img_dev", "Artifact", "Private container images (dev)")


def _technology_outside_ovhcloud(m: Builder):
    """Elements: technology: outside ovhcloud."""
    el = m.el
    el("n_csc", "Node", "Copernicus stations (CADIP, AUXIP, PRIP) - HTTPS endpoints")
    el("n_dataspaces", "Node", "CDSE and DestinE EarthDataHub - HTTPS endpoints")
    el("n_ghcr", "Node", "Public container registries (ghcr.io, docker.io, quay.io)")
    el("n_letsencrypt", "Node", "Let's Encrypt (ACME certificate authority)")
    el("n_eopf_gitlab", "Node", "EOPF GitLab (gitlab.eopf.copernicus.eu)")
    el("n_dns", "Node", "Public DNS (rs-python.eu zone)")
    el("g_ext", "Grouping", "External services (Internet)")
    el("g_admin", "Grouping", "Administration sites (IP whitelist)")
    el("l_company", "Location", "Company site (public IP whitelisted)")
    el("l_contractor", "Location", "Contractor site (public IP whitelisted)")
    el("l_users", "Location", "Anywhere (Internet)")
    el(
        "dv_laptop_company",
        "Device",
        "Project laptops (company) - latest Ubuntu LTS, full-disk encryption",
        "Secured project laptops (physical security and disk encryption), the only workstations allowed for the "
        "development and operation activities.",
    )
    el(
        "dv_laptop_contractor",
        "Device",
        "Project laptops (contractor) - latest Ubuntu LTS, full-disk encryption",
        "Secured project laptops (physical security and disk encryption), the only workstations allowed for the "
        "development and operation activities.",
    )
    el("dv_enduser", "Device", "End-user workstations (web browser, rs-client, S3 client)")
    el("g_inet", "Grouping", "Internet zone")
    for env in ("ops", "dev"):
        el(f"g_pub_{env}", "Grouping", f"Public zone ({env}) - Ext-Net, public IP addresses")
        el(f"g_priv_{env}", "Grouping", f"Private zone ({env})")
    el("nw_internet", "CommunicationNetwork", "Internet")


def _functional_packages(m: Builder):
    """Elements: functional packages."""
    el = m.el
    for package in FUNCTIONAL_PACKAGES:
        el(package.key, "ApplicationFunction", package.name, package.description, components=package.components)
        for i, (fname, fdesc) in enumerate(package.functions):
            el(f"{package.key}_{i}", "ApplicationFunction", fname, fdesc)
