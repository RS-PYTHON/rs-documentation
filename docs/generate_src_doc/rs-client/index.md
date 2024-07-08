# Python API Library for RS-Client

This is the generated documentation from the source code. It is divided into 2 sections, the documentation for RS-Client
libraries and the documentation for the already implemented Prefect flows that use the RS-Client instances to access the RS-Server endpoints.

## RS-Client Classes

Documentation for RS-Client: [rs-client](rs_client.md)

## RS-Client Workflows

Currently, there are 3 Prefect flows implemented that use the a RS-Client instance to access the RS-Server 
endpoints:

* an [Example](example.md) prefect flow 
* a prefect flow that stages the files from a CADIP server or from an ADGS server: [Staging](staging.md)
* a prefect flow specifically implemented for processing [S1 L0](s1_l0.md) products.
