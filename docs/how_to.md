This procedure is run automatically in the CI by the *generate
documentation* workflow. It can be executed also locally to verify the
generated documentation (before publishing it for example).

See the [description](description.md) for more details on the
process and technical stuff.

Prerequisites
=============

The following have to be installed
- python version 3.11
- poetry at least version 1.7.1

Prepare the environment
=======================
1. Clone the rs-documentation repository:   
```shell
git clone https://github.com/RS-PYTHON/rs-documentation.git
cd rs-documentation
```

2. Clone the RS-Server, RS-Client, RS-Demo, RS-Infrastructure and RS-Helm repositories. The default branch from which 
the projects are pulled is 'develop', but one can choose whatever branch is needed by using '-b' flag.

    **NOTE**: The repositories need to be pulled in 'docs' directory

    **NOTE**: The RS-Demo, RS-Infrastructure and RS-Helm repositories are not public, so a github access is needed
```shell
cd docs
git clone -b develop https://github.com/RS-PYTHON/rs-server.git
git clone -b develop https://github.com/RS-PYTHON/rs-client-libraries.git
git clone -b develop git@github.com:RS-PYTHON/rs-demo.git
git clone -b develop git@github.com:RS-PYTHON/rs-infrastructure.git
git clone -b develop git@github.com:RS-PYTHON/rs-helm.git
cd ..
```

3. Install needed rs-documentation packages:
```shell
poetry install
```

Generate and integrate the documentation
========================================

From the **rs-documentation directory**, execute the command:
```shell
poetry run mkdocs build
```

This command generates the html pages of all the technical documentation as well as for the static documentation
and write them in the **site** directory.

Verify the generated documentation
==================================

The documentation is generated in the directory "site". The main page is the file "index.html" is this
folder. It can be open in a web browser for example.

The REST API can’t be opened like that since it needs to be served. You
can open the REST API locally starting the rs-server and connecting to
the /docs endpoint.

You can verify the generated documentation before publishing it. mkdocs may be used to serve the generated site:
```shell
poetry run mkdocs serve
```

Important elements to check :

-   the python api is accessible in the technical documentation

-   the python api is well formatted

-   the rest api is accessible in the technical documentation

-   the rest api is well formatted

-   …
