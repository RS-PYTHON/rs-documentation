site_name: RS-Python
#site_url: https://rs-python.github.io/rs-documentation/
# Copyright
copyright: Copyright &copy; 2024-2026, Airbus, CS Group

theme:
  name: material
  custom_dir: docs/_templates
  features:
    - navigation.tabs
    - navigation.tabs.sticky
    - navigation.sections
    - navigation.top
    - navigation.tracking
    - navigation.indexes
    - navigation.path
    - toc.integrate
    - toc.follow
    - search.suggest
    - search.highlight
    - content.tabs.link
    - content.code.annotation
    - content.code.copy
  language: en
  logo: _static/rspython_logo.png
  favicon: _static/rspython_logo.png
  palette:
    - scheme: default
      toggle:
        icon: material/toggle-switch-off-outline
        name: Switch to dark mode
      primary: teal
      accent: purple
    - scheme: slate
      toggle:
        icon: material/toggle-switch
        name: Switch to light mode
      primary: teal
      accent: lime
markdown_extensions:
  - sane_lists
  - admonition
  - pymdownx.details
  - pymdownx.superfences
extra_css: [_templates/style.css]
plugins:
  - search
  - mkdocstrings:
      handlers:
        python:
          options:
            extra:
              separate_modules: true

nav:
- Home:
  - index.md
  - Generate Documentation: how_to.md

- RS-Server:
  - rs-server/docs/doc/index.md
  - User Manual:
    - rs-server/docs/doc/users/index.md
    - Overall Architecture: rs-server/docs/doc/users/architecture.md
    - Main Functionalities: rs-server/docs/doc/users/functionalities.md
    - Catalog: rs-server/docs/doc/users/catalog.md
    - OAuth2 and API Key Manager: rs-server/docs/doc/users/oauth2_apikey_manager.md
  - Developer Manual:
    - General Description: rs-server/docs/doc/dev/developer_manual.md
    - Installation: rs-server/docs/doc/dev/installation.md
    - Project Structure: rs-server/docs/doc/dev/project-structure.md
    - Good Practices:
      - Code style: rs-server/docs/doc/dev/good_practices/code-style.md
      - Workflow: rs-server/docs/doc/dev/good_practices/workflow.md
      - CI: rs-server/docs/doc/dev/good_practices/ci.md
    - Rest API:
      - rs-server/docs/doc/dev/rest_api/swagger_index.md
  - Python Documentation:
$RS_SERVER_PYDOC

- RS-Client:
  - rs-client-libraries/docs/doc/index.md
  - Python Documentation:
$RS_CLIENT_LIBRARIES_PYDOCS

- RS-DPR-Service:
  - rs-dpr-service/docs/doc/index.md
  - Python Documentation:
$RS_DPR_SERVICE_PYDOCS

- RS-Notebooks:
  - rs-demo/doc/index.md
  - Running Modes: rs-demo/README.md

- RS-Deployment:
  - rs_deployment_start.md
  - Infrastructure Deployment:
    - rs-infra-core/README.md
    - Installation: rs-infra-core/docs/installation.md
    - Cluster Management: rs-infra-core/docs/how-to/Cluster Management.md
    - Cluster start and stop: rs-infra-core/docs/how-to/Cluster start and stop.md
    - Dask Gateway : rs-infra-core/docs/how-to/Dask-gateway.md
    - GitHub container registry: rs-infra-core/docs/how-to/GitHub Container Registry.md
    - Ingress controller: rs-infra-core/docs/how-to/Ingress.md
    - Prefect worker: rs-infra-core/docs/how-to/Prefect-Worker.md
    - Remote kubectl: rs-infra-core/docs/how-to/Remote kubectl.md
    - Restore database with CloudNativePG : rs-infra-core/docs/how-to/Restore database with CloudNativePG.md
    - Velero Backup and Restore : rs-infra-core/docs/how-to/Velero_Backup-Restore.md
    - Wazuh Server installation: rs-infra-core/docs/how-to/Wazuh server install.md
  - Applications Deployment:
    - RS-Server deployment: rs-helm/README.md
  - Monitor Object Storage access:
    - Deploy flow collect-obs-logs: rs-client-libraries/docs/quota_monitoring/setting_quota_feature.md
  - Third-party dependencies:
    - Core infrastructure FOSS: rs-infra-core/NOTICE.md
    - Monitoring FOSS: rs-infra-monitoring/NOTICE.md
    - Workflow env. FOSS: rs-workflow-env/NOTICE.md
