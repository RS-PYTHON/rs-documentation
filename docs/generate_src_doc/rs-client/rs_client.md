# API Clients Documentation

This documentation provides an overview of the various API clients available in the `rs_client` package. Each client is designed to interact with specific services and provide a convenient way to access their functionalities.  

<span style="font-size: 1.5em; color: green;">RsClient</span>
::: rs_client.rs_client.RsClient
This client is a general client used for interacting with the RS service. It can be used to retrieve a specific client, see below.

<span style="font-size: 1.5em; color: green;">StagingClient</span>
::: rs_client.ogcapi.staging_client.StagingClient
This client allows you to interact with the the RS-Server Staging service, making it easy to stage files from external stations CADIP/AUXIP. It inherits the RsClient class

<span style="font-size: 1.5em; color: green;">StacBase</span>
::: rs_client.stac.stac_base.StacBase
The StacBase class serves as a foundational implementation for interacting with a STAC (SpatioTemporal Asset Catalog) API to provide a robust interface for retrieving collections, items, and queryables, as well as performing searches. It inherits the RsClient class

<span style="font-size: 1.5em; color: green;">AuxipClient</span>
::: rs_client.stac.auxip_client.AuxipClient
The AuxipClient is tailored for accessing the AUXIP service. It includes functionalities for querying auxiliary data and metadata from an external AUXIP station. It inherits the StacBase class

<span style="font-size: 1.5em; color: green;">CadipClient</span>
::: rs_client.stac.cadip_client.CadipClient
CadipClient is designed to interface with the CADIP service. It includes functionalities for querying data and metadata from an external CADIP station. It inherits the StacBase class

<span style="font-size: 1.5em; color: green;">CatalogClient</span>
::: rs_client.stac.catalog_client.CatalogClient
This client allows you to interact with the STAC service, making it easy to search, retrieve, and manage spatio-temporal asset catalog data. It inherits the StacBase class

For detailed usage instructions and examples for each client, please refer to the respective sections.
