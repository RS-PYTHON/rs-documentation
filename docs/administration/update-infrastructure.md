# Update infrastructure parameters

All the infrastructure parameters are variables of your Ansible **inventory** (see
[Infrastructure installation](../rs-infra-core/docs/installation.md)):

| File of the inventory | Content |
|---|---|
| `host_vars/setup/main.yaml` | Domain name, cloud provider credentials, S3 endpoints... |
| `host_vars/setup/apps.yml` and `host_vars/setup/apps/*.yaml` | Parameters of each application: Keycloak, databases, Prefect, JupyterHub, Dask, rs-server... |
| `cluster.tfvars` | Node pools sizing and autoscaling, network, S3 buckets created by Terraform. |
| `openrc.sh` | OpenStack credentials. |
| `hosts.yaml` | Ansible hosts and Python interpreters. |

To modify the configuration of a running platform:

1. Modify the variables in your inventory. Keep your inventory under version control.
2. Regenerate the inventory: `ansible-playbook generate_inventory.yaml -i inventory/mycluster/hosts.yaml`.
   The credentials that were already generated are kept, see [Credentials](../rs-infra-core/docs/how-to/credentials.md).
3. Redeploy the impacted application(s), from the bastion:

    ```shell
    ansible-playbook apps.yaml -i inventory/mycluster/hosts.yaml \
        -e '{"package_paths": ["~/<repository>/apps/"]}' -e app=<application>
    ```

    where `<repository>` is the repository that contains the application (`rs-infra-core`, `rs-infra-monitoring`,
    `rs-workflow-env`, `rs-server-deployment` or `rs-workflow-deployment`) and `<application>` the name of the
    application folder without its `NN-` prefix.

4. For the node pools, run the Terraform part again: `ansible-playbook cluster.yaml -i inventory/mycluster/hosts.yaml`
   (see [Cluster management](../rs-infra-core/docs/how-to/cluster-management.md)).

Most applications read their configuration (config maps, secrets) only when their pods start: restart them after the
update if needed, e.g. `kubectl -n <namespace> rollout restart deployment <name>`.

To upgrade the version of a component, update its version in the `kustomization.yaml` or `values.yaml` file of the
application (Helm chart version, Docker image tag), then redeploy it the same way.

To remove an application, see [Remove an application](../rs-infra-core/docs/how-to/remove-applications.md).
