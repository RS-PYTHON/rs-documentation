# Run existing flows

The flows delivered by default are deployed by the administrators in each
[Prefect](../services/virtual-environment/prefect.md) instance. They are listed in the
[Prefect flows](../rs-client-libraries/docs/doc/flows/index.md) section. This page shows how to run one of them from
the Prefect dashboard, with the example of the Level-0 processing of a Sentinel-3 acquisition session.

## 1. Find the input data

The Level-0 processing takes as input an acquisition session of a CADIP station. To find the sessions available
in the stations, use one of:

- the CADIP [STAC browser](../services/browse-products.md#stac-browsers), e.g.
  <https://stac-browser-cadip.ops.rs-python.eu>,
- the `/cadip/search` endpoint of the [Swagger page](../services/swagger.md),
- the `Search Cadip` Prefect deployment (`search-cadip` flow),
- Python code, see [Browse products](../services/browse-products.md#with-python).

Note the session identifier, e.g. `S3A_20260807020505053186`.

## 2. Run the flow

1. Open the Prefect dashboard, e.g. <https://processing.ops.rs-python.eu/dashboard>, and go to the
   *Deployments* page. Use the tags to filter the deployments, e.g. `processing` and `l0`.
2. Open the `process-l0/Process L0` deployment and click *Run > Custom run*.
3. Fill in the parameters:

    - `session`: the session identifier found above.
    - `flow_params`: leave it empty to use the default settings of the platform (the processor, the Dask cluster,
      the target collections... see [Level-0 flows](../rs-client-libraries/docs/doc/flows/level0-flows.md)), or
      override some of them, e.g. set `owner_identifier` to your login to write the products in your own
      collections.

4. Click *Submit*. A new flow run is created. See the
   [Prefect documentation](https://docs.prefect.io/v3/how-to-guides/deployments/run-deployments) for more ways to
   run a deployment.

!!! tip

    Use *Quick run* instead of *Custom run* to run a deployment with its default parameters.

## 3. Monitor the flow run

The flow run page shows:

- the **logs** of the flow and of its tasks. The Level-0 flow first looks for the session in the catalog, stages
  it from the CADIP station if needed, then calls the generic processing flow (`process-generic`). The logs of the
  processing contain the link to the [Dask dashboard](../services/virtual-environment/dask.md) of the processor
  run, and the command to [cancel the run](../rs-dpr-service/docs/doc/cancel-dpr-run.md) if needed.
- the **sub-flow runs** and **task runs** with their status,
- the **artifacts**, e.g. `dpr-task-table` and `dpr-payload` that show the processor
  [task table and payload file](../rs-client-libraries/docs/doc/flows/tasktable-payload.md).

Lower-level information (logs, traces, resources consumption) is available in Grafana, see
[Troubleshooting](../advanced/troubleshooting.md).

## 4. Look at the results

When the flow run is completed, the generated products are stored in the object storage and registered as STAC
items in the catalog collections configured for the flow. Browse them with the catalog
[STAC browser](../services/browse-products.md#stac-browsers), e.g.
<https://stac-browser-catalog.ops.rs-python.eu/>, and download them as described in
[Browse products](../services/browse-products.md#download-the-assets).

## Going further

- [Prefect flows](../rs-client-libraries/docs/doc/flows/index.md): all the flows delivered by default and their
  parameters.
- [Systematic processing](../rs-client-libraries/docs/doc/advanced/systematic-processing.md): how the flows are
  chained automatically.
- [Create a custom flow](../rs-client-libraries/docs/doc/advanced/custom-flow.md): write your own flows.
