# Administration

This section is dedicated to the RS-Python **administrators**. It assumes a good knowledge of
[Kubernetes](https://kubernetes.io/docs/home/), [Helm](https://helm.sh/docs/), [Ansible](https://docs.ansible.com/),
[Terraform](https://developer.hashicorp.com/terraform/docs) and [Keycloak](https://www.keycloak.org/documentation).

The administrators are present during the whole project lifetime, not only during the development phase. Their
tasks are:

| Task | Documentation |
|---|---|
| Deploy the platform from scratch: Kubernetes cluster, infrastructure, monitoring, virtual environment, RS-Python services and flows. | [Deploy RS-Python](deploy.md) |
| Modify the configuration of a running platform. | [Update infrastructure parameters](update-infrastructure.md), [Update rs-server parameters](update-rs-server.md) |
| Add users, assign and synchronise their rights. | [Create accounts and assign permissions](accounts-permissions.md) |
| Initialise the processing environment of a user group after the deployment: Prefect blocks and variables, Dask clusters, default flows. | [Initialise the processing environment](init-processing-environment.md) |
| Monitor the platform: logs, metrics, traces, resources and costs, to troubleshoot errors and bad performances. | [Monitoring and observability](monitoring.md), [Object storage quota monitoring](../rs-client-libraries/docs/doc/operation/quota-monitoring.md), [Performance indicators](../rs-client-libraries/docs/doc/operation/performance-indicators.md) |
| Operate the cluster: start and stop, backup and restore, credentials... | *Operations how-to* pages of the navigation menu, from [rs-infra-core](../rs-infra-core/README.md) |
| Support the users who face difficulties. | [Troubleshooting](../advanced/troubleshooting.md) |

The **operators** use a subset of these tools, mainly the monitoring ones, to check the health of the system and
the completeness and timeliness of the production.

## Administration use cases

![Infrastructure use cases](../images/use-cases-infrastructure.svg)

The deployment use cases are described in [Deploy RS-Python](deploy.md).
