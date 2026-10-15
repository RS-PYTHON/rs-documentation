# rs-documentation

System-level documentation of [RS-Python](https://home.rs-python.eu/rs-documentation/), and generator of its
documentation website.

## Overview

RS-Python is a set of services and tools to process the data of the [Copernicus](https://www.copernicus.eu/)
[Sentinel](https://sentinels.copernicus.eu/) missions: access to the ground stations, catalog of the products,
processing with the DPR processors orchestrated by [Prefect](https://www.prefect.io/) and [Dask](https://www.dask.org/),
on a [Kubernetes](https://kubernetes.io/) cluster or on your computer.

This repository contains:

- the system-level pages ([docs](docs)): getting started, services, administration, architecture, CI/CD,
  glossary...,
- the [MkDocs](https://www.mkdocs.org/) configuration that aggregates them with the documentation of all the other
  RS-PYTHON repositories, and with the Python API documentation generated from the docstrings,
- the GitHub workflow that publishes the website at <https://home.rs-python.eu/rs-documentation/>.

## Getting started

Read the documentation online: <https://home.rs-python.eu/rs-documentation/>.

To generate the website locally, see
[Generate the documentation](docs/developers/generate-documentation.md#generate-the-website-locally).

## Documentation

- [Home page](docs/index.md)
- [Getting started](docs/getting-started/project-organisation.md)
- [Administration](docs/administration/index.md)
- [Developers and contributors](docs/developers/index.md)
- [Generate the documentation](docs/developers/generate-documentation.md)

## Related repositories

All the documented repositories are listed in [Project organisation](docs/getting-started/project-organisation.md),
e.g. [rs-server](https://github.com/RS-PYTHON/rs-server), [rs-client-libraries](https://github.com/RS-PYTHON/rs-client-libraries),
[rs-dpr-service](https://github.com/RS-PYTHON/rs-dpr-service) and [rs-infra-core](https://github.com/RS-PYTHON/rs-infra-core).

## Contributing

See the [contribution guidelines](docs/developers/contributing.md).
Report bugs in the [issue tracker](https://github.com/RS-PYTHON/rs-documentation/issues). In case of sensitive bugs like
security vulnerabilities, please contact <ops_coprs@airbus.com> directly instead of using the issue tracker.

## Licensing

The code in this project is licensed under the [Apache License, Version 2.0](https://www.apache.org/licenses/LICENSE-2.0).

---

![](https://raw.githubusercontent.com/RS-PYTHON/.github/refs/heads/main/profile/banner_logo.jpg)

This project is funded by the EU and ESA.
