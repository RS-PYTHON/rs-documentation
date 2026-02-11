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
```shell
cd docs
for repo in rs-server rs-client-libraries rs-demo rs-dpr-service rs-infra-core rs-infra-monitoring rs-workflow-env rs-helm ; do
  git clone -b develop https://github.com/RS-PYTHON/${repo}.git
done
cd ..
```
**Option 2:** If you already have those repositories in your workspace, just create symbolic links to them:
```shell
cd docs
for repo in rs-server rs-client-libraries rs-demo rs-dpr-service rs-infra-core rs-infra-monitoring rs-workflow-env rs-helm ; do
  ln -s /path/to/your/workspace/${repo} ${repo}
done
cd ..
```

3. Install needed rs-documentation packages:
```shell
poetry install
```

Generate and integrate the documentation
========================================

From the **rs-documentation directory**, run the script *.github/scripts/generate_mkdocs.sh*:
```shell
./.github/scripts/generate_mkdocs.sh
```

This script will automatically scan the Python projects in your environment and generate their documentation. After executing the script, you should see a newly generated *mkdocs.yml* file, that contains the summary used by mkdocs to generate the website.

Once this file is generated, execute the command:
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
