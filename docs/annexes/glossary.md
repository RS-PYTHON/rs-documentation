# Glossary

| Term | Definition |
|---|---|
| **ADF** | Auxiliary Data File: auxiliary file used by a processor, e.g. an orbit file or a calibration file. |
| **ADGS** | Auxiliary Data Gathering Service: the Copernicus service that provides the auxiliary data, through an AUXIP interface. |
| **API key** | A secret token created with the API Key Manager, that carries the identity and the rights of a user, used to call the services. See [User rights and API keys](../getting-started/user-rights.md#api-keys). |
| **ARD** | Analysis Ready Data, e.g. the Sentinel-1 ARD processor. |
| **Asset** | In STAC, a file of an item, with its location. |
| **AUXIP** | AUXiliary data Interface delivery Point: OData interface to get the auxiliary data. |
| **CADIP** | CADU Interface delivery Point: OData interface of the acquisition ground stations, to get the raw data acquired by the satellites, organised in sessions. |
| **CADU** | Channel Access Data Unit: raw telemetry data downlinked by the satellites. |
| **CDSE** | [Copernicus Data Space Ecosystem](https://dataspace.copernicus.eu/): the platform that distributes the Copernicus data. |
| **Collection** | In STAC, a group of items. |
| **CPM** | [Core Python Modules](https://cpm.pages.eopf.copernicus.eu/eopf-cpm/main/index.html) of EOPF, used by the processors. |
| **CQL2** | [Common Query Language](https://docs.ogc.org/is/21-065r2/21-065r2.html): the language of the STAC API filters. |
| **CSC** | Copernicus Space Component: the space and ground segments of Copernicus. |
| **Dask** | [Python library](https://www.dask.org/) for parallel computing, used to run the processors and the staging. |
| **DEM** | Digital Elevation Model. |
| **Deployment** (Prefect) | A flow made runnable on the platform workers, from the dashboard, an automation or another flow. |
| **DPR** | Data PRocessor: the re-engineered Sentinel processors, developed by the EOPF project. |
| **EDRS** | European Data Relay System. |
| **EOPF** | [Earth Observation Processing Framework](https://eopf.copernicus.eu/): the ESA project that re-engineers the Sentinel processors in Python. |
| **Flow** (Prefect) | A Python function decorated with `@flow`, that implements a workflow. |
| **Item** | In STAC, a product described by its metadata, footprint and assets. |
| **Keycloak** | The [identity and access management](https://www.keycloak.org/) solution of RS-Python. |
| **Local mode** | Mode where RS-Python runs on a single computer with Docker Compose, for development purposes. |
| **Cluster mode** | Nominal mode where RS-Python runs on a Kubernetes cluster. |
| **LTA** | Long Term Archive. |
| **NRT, NTC, STC** | Near Real Time, Non Time Critical and Short Time Critical timeliness of the products. |
| **OData** | [Open Data Protocol](https://www.odata.org/), used by the Copernicus stations. |
| **OGC** | [Open Geospatial Consortium](https://www.ogc.org/), that publishes the OGC API standards. |
| **OSAM** | Object Storage Access Manager: the service that manages the object storage accounts and rights of the users. |
| **Owner** | The user that owns a catalog collection. |
| **Payload file** | The file that describes a processor run: units, inputs, outputs, storage... See [Task tables and payload file](../rs-client-libraries/docs/doc/flows/tasktable-payload.md). |
| **PRIP** | Production service Interface delivery Point: OData interface of the production services, to get the Level-0, Level-1 and Level-2 products. |
| **RS-Python, RSPY** | Reference System Python: this project. |
| **Session** | A CADIP acquisition session: the raw data received by a ground station during one pass of a satellite. |
| **Staging** | Copy of products from an external data source into the RS-Python object storage and catalog. |
| **STAC** | [SpatioTemporal Asset Catalog](https://stacspec.org/): the specification used to describe all the data. |
| **Task table** | The file delivered with a processor, that describes its processing units, pipelines, inputs, outputs and auxiliary data selection rules. |
| **Work pool** (Prefect) | A group of Prefect workers that execute the flow runs. |
