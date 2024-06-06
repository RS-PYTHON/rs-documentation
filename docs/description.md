Introduction
============

TO BE UPDATED !

The rs-server technical documentation is mainly written using
markdown. The python API documentation is built using mkdocs functionalities while the
REST API documentation is built using fastapi functionalities.

Therefore, the built procedure includes specific steps to handle these
elements. The technical documentation include links to open the python
api and rest api reference guides.

Python api reference guide
==========================

The python api is generated using
[mkdocs](https://www.mkdocs.org/) functionalities. It
enables us to generate a reference guide from python doc-strings.

A link to this reference guide is added in the technical documentation.

Rest api reference guide
========================

The REST API is provided by FastAPI on a dynamic way on the /docs
endpoint, using SwaggerUI functionalities. The technical documentation
should also be provided statically in the technical documentation.
FastAPI enables us to export the openapi specification in a json format.
Using Swagger UI functionalities, we can generate a static REST API
documentation.

It takes the form of an HTML index file using swagger for the rendering
and the exported openapi file for the content.

To provide a link to this REST API from the technical documentation, the
same trick is used than the one used for the python API.
