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

2. Create an access to the project repositories in the docs subfolder. You can chose one of the two following ways:   
**Option 1:** Clone the RS-Server, RS-Client, RS-DPR-Service, RS-Demo, RS-Infra-Core and RS-Helm repositories. The default branch from which 
the projects are pulled is 'develop', but one can choose whatever branch is needed by using '-b' flag.

    **NOTE**: The repositories need to be pulled in 'docs' directory

    **NOTE**: The RS-Demo, RS-Infra-Core and RS-Helm repositories are not public, so a github access is needed
```shell
cd docs
git clone -b develop https://github.com/RS-PYTHON/rs-server.git
git clone -b develop https://github.com/RS-PYTHON/rs-client-libraries.git
git clone -b develop https://github.com/RS-PYTHON/rs-dpr-service.git
git clone -b develop git@github.com:RS-PYTHON/rs-demo.git
git clone -b develop git@github.com:RS-PYTHON/rs-infra-core.git
git clone -b develop git@github.com:RS-PYTHON/rs-helm.git
cd ..
```
**Option 2:** If you already have those repositories in your workspace, just create symbolic links to them:
```shell
cd docs
ln -s /path/to/your/workspace/rs-server rs-server
ln -s /path/to/your/workspace/rs-client-libraries rs-client-libraries
ln -s /path/to/your/workspace/rs-dpr-service rs-dpr-service
# etc...
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
and writes it in the **site** directory.

Verify the generated documentation
==================================

The documentation is generated in the "site" directory. The main page is the "index.html" file located within
this folder, which can be opened in a web browser, for example.

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
