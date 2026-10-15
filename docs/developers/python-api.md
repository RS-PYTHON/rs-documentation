# Python API documentation

The Python API documentation is generated automatically from the docstrings of the source code, with
[mkdocstrings](https://mkdocstrings.github.io/). It is available for:

| Project | Modules |
|---|---|
| [rs-server](../rs-server/docs/doc/index.md) | `rs_server_adgs`, `rs_server_cadip`, `rs_server_catalog`, `rs_server_common`, `rs_server_frontend`, `rs_server_osam`, `rs_server_prip`, `rs_server_staging` |
| [rs-client-libraries](../rs-client-libraries/docs/doc/index.md) | `rs_client`, `rs_common`, `rs_workflows` |
| [rs-dpr-service](../rs-dpr-service/docs/doc/index.md) | `rs_dpr_service` |

Browse the modules from the navigation menu.

The docstrings are written in the [Google style](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings),
with Markdown formatting. See [Generate the documentation](generate-documentation.md) to generate this
documentation locally.

The documentation of the HTTP endpoints of the web services is not generated here, but in the
[Swagger page](../services/swagger.md), from the OpenAPI specification of the services.
