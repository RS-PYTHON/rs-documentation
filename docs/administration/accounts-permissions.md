# Create accounts and assign permissions

The user accounts and their rights are managed in [Keycloak](https://www.keycloak.org/), the identity and access
management solution of RS-Python. All the user rights are set in this single location, and are used by all the
RS-Python services. See the [Keycloak Server Administration Guide](https://www.keycloak.org/docs/latest/server_admin/index.html).

Open the Keycloak administration console, e.g. <https://iam.ops.rs-python.eu/admin> on the reference platform, and
select the RS-Python realm (`rspy` by default).

## Create a user account

1. Go to *Users > Add user*, fill in the user name, e-mail, first and last names, and click *Create*.
2. In the *Credentials* tab, set a temporary password: the user will have to change it at the first login.
3. In the *Groups* tab, add the user to the groups that give access to the applications of the virtual
   environment, e.g. `RS-JUPYTER-USER` for JupyterHub and Prefect, and `RS-ADMIN` for the administrators (see
   [Applications](../getting-started/user-rights.md#applications)).

The user name is also the **owner** of the user's catalog collections and the name of the user's Prefect block
(`env-vars-<user name>`).

## Assign permissions

In the *Role mapping* tab of the user (or of a group, to give the same rights to several users), click
*Assign role* and select the realm roles described in [User rights](../getting-started/user-rights.md#available-rights):

- the roles on the catalog collections, e.g. `rs_catalog_copernicus:*_read`,
- the roles on the stations, e.g. `rs_cadip_sgs_read`, `rs_auxip_adgs_read`, `rs_prip_s1a_read`,
- the landing page roles needed by the STAC browsers, e.g. `rs_cadip_landing_page`,
- the staging roles, e.g. `rs_processes_staging_execute`, `rs_processes_staging_download_sgs`,
- `rs_osam_update` for the administrators.

If a role does not exist yet (e.g. for a new collection), create it in *Realm roles > Create role*. Use
[composite roles](https://www.keycloak.org/docs/latest/server_admin/index.html#con-composite-roles_server_administration_guide)
to group roles, e.g. `rs_cadip_all_read` with all the CADIP station roles.

The roles are taken into account at the next login of the user. For the API keys, the services ask the API Key
Manager for the current roles of the key owner, and cache the answer for a few minutes.

To delete or deactivate a user, delete the user or disable it in its *Details* tab. Its API keys are not usable
anymore.

## Synchronise the object storage rights

The users download the products directly from the S3 object storage, with personal credentials. The
[OSAM](../rs-server/docs/doc/users/osam.md) service keeps their object storage accounts and rights consistent with
their Keycloak accounts and roles:

- `POST /storage/accounts/update` creates the object storage accounts of the new Keycloak users and deletes the
  accounts of the deleted users,
- `POST /storage/account/{user}/update` computes and applies the object storage rights of a user, from its catalog
  roles and from the [bucket configuration](update-rs-server.md#object-storage-buckets-and-data-lifecycle).

These endpoints require the `rs_osam_update` role. They are called:

- periodically by OSAM itself (twice a day by default),
- by the `Synchronize OSAM Accounts` and `Update OSAM Account` Prefect deployments (`operation` and `osam` tags),
  that you can run after creating a user or modifying its roles,
- or manually from the [Swagger page](../services/swagger.md).

## Export and import the realm

To copy the roles and the clients of a realm to another platform, see
[Keycloak realm export and import](../rs-infra-core/docs/how-to/keycloak-realm-export-import.md).
