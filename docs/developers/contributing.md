# Contributing

Contributions to RS-Python are welcome: bug reports, documentation improvements, code changes... This page
describes the contribution guidelines, common to all the RS-PYTHON repositories.

## Report an issue

Report bugs and request features in the issue tracker of the relevant
[GitHub repository](../getting-started/project-organisation.md#source-code-organisation). Give the version you use,
the steps to reproduce the problem, and the expected and actual behaviours.

In case of sensitive bugs like security vulnerabilities, please contact <ops_coprs@airbus.com> directly instead
of using the issue tracker. We value your effort to improve the security and privacy of this project!

## Contribute code or documentation

1. Set up your [coding environment](coding-environment.md).
2. Create a branch from `develop`, named `feat-<ticket-id>/<short-description>` for a feature, e.g.
   `feat-rspy123/staging-retries`, or `fix/<short-description>` for a fix.
3. Make your changes, with:
    - unit tests (and integration tests if relevant),
    - the documentation, in the same pull request (see [Generate the documentation](generate-documentation.md)),
    - a new entry in the `CHANGELOG.md` file of the repository, if it has one.
4. Check that the code quality checks pass: `poetry run pre-commit run --all-files` and the tests.
5. Push your branch and open a [pull request](https://docs.github.com/en/pull-requests) to `develop`. The CI runs
   the checks, the tests and SonarQube. Fix the issues it reports.
6. A team member reviews your pull request, then merges it.

To test changes that impact several repositories, use the same branch name in all of them: the CI of the
[documentation](generate-documentation.md) and of the demos use the branch with the same name when it exists.

### Commit messages

Write the commit messages following the [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/)
specification and [these best practices](https://cbea.ms/git-commit/), e.g.
`feat(catalog): add the PATCH collection endpoint`.

## Code style

- Follow [PEP 8](https://peps.python.org/pep-0008/). The code is formatted by [black](https://black.readthedocs.io/)
  and [isort](https://pycqa.github.io/isort/), with a line length of 120 characters.
- Add type annotations, checked by [mypy](https://mypy-lang.org/).
- Write docstrings in the [Google style](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings),
  with Markdown formatting: they are used to generate the [Python API documentation](python-api.md).
- Add the license header at the start of each new source file:

    ```python
    # Copyright 2023-2026 Airbus, CS Group
    #
    # Licensed under the Apache License, Version 2.0 (the "License");
    # you may not use this file except in compliance with the License.
    # You may obtain a copy of the License at
    #
    #     http://www.apache.org/licenses/LICENSE-2.0
    #
    # Unless required by applicable law or agreed to in writing, software
    # distributed under the License is distributed on an "AS IS" BASIS,
    # WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    # See the License for the specific language governing permissions and
    # limitations under the License.
    ```

- Mark the tests with `@pytest.mark.unit` or `@pytest.mark.integration`.

The checks run by [pre-commit](https://pre-commit.com/) before each commit and by the CI are:

| Check | Tool |
|---|---|
| Formatting, end of files, trailing spaces, merge conflicts, TOML and YAML syntax | pre-commit hooks, black, isort |
| License headers | [addlicense](https://github.com/google/addlicense), [SkyWalking Eyes](https://github.com/apache/skywalking-eyes) |
| Linting | [Pylint](https://pylint.readthedocs.io/), [Flake8](https://flake8.pycqa.org/) |
| Typing | [mypy](https://mypy-lang.org/) |
| Security | [Bandit](https://bandit.readthedocs.io/), [Safety](https://safetycli.com/), [Trivy](https://trivy.dev/) |
| Tests and coverage | [pytest](https://docs.pytest.org/) |
| Quality report | [SonarQube](https://www.sonarsource.com/products/sonarqube/) |

## Definition of Done

A change is done when:

- the code covers the functionality, with unit tests (and integration tests if relevant), and all the tests pass,
- the documentation is updated: Markdown pages, docstrings, OpenAPI descriptions of the endpoints,
- the changelog is updated,
- the CI checks are green and the SonarQube issues are fixed,
- the code has been reviewed by a team member.

## Code of conduct

We are committed to making participation in this project a harassment-free experience for everyone. All the
contributors are expected to follow the [Contributor Covenant Code of Conduct](https://www.contributor-covenant.org/version/2/1/code_of_conduct/):
be respectful, welcoming and constructive, focus on what is best for the community, and accept constructive
criticism. Unacceptable behaviour may be reported to <ops_coprs@airbus.com>.

## License

By contributing, you agree that your contributions are licensed under the
[Apache License, Version 2.0](https://www.apache.org/licenses/LICENSE-2.0), like the rest of the project.
