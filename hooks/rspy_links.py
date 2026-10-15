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

"""MkDocs hooks of the RS-Python documentation.

The main hook turns absolute GitHub links between RS-PYTHON repositories into site-internal links.

The Markdown files of each RS-PYTHON repository are written to be read both on GitHub and in this
documentation website. To link a page of another repository, authors use its absolute GitHub URL, e.g.
``https://github.com/RS-PYTHON/rs-server/blob/develop/docs/doc/users/catalog.md#search``.

When the target page is part of this website (because the repository is cloned under ``docs/``), the URL
is replaced by a relative link to the local page, so that:

- the reader stays inside the documentation website,
- MkDocs validates the link and the anchor at build time.

Links to pages that are not part of the website (source code, folders, ...) are left untouched.

Conversely, the relative links of a repository to its own source code (e.g. ``[apps](apps)`` in a README)
work on GitHub but not in the website, that only contains the Markdown pages and the images. They are
replaced by the absolute GitHub URL of their target.
"""

import logging
import os
import posixpath
import re

log = logging.getLogger("mkdocs.hooks.rspy_links")

# https://github.com/RS-PYTHON/<repo>/(blob|tree)/<branch>/<path>[#anchor]
GITHUB_LINK = re.compile(
    r"https://github\.com/RS-PYTHON/(?P<repo>[\w.-]+)/(?:blob|tree)/(?:develop|main)/"
    r"(?P<path>[^\s)#\"'<>]+\.md)(?P<anchor>#[^\s)\"'<>]*)?",
)

# Relative inline links: [text](target "title") or ![alt](target)
RELATIVE_LINK = re.compile(
    r"(?P<prefix>\]\()(?P<target>(?![a-zA-Z][\w+.-]*:|#|/)[^)\s]+)(?P<suffix>(?:\s+\"[^\"]*\")?\))",
)

# Fenced code blocks and inline code spans, where the links must not be modified
CODE = re.compile(r"(?:^[ \t]*(```|~~~).*?^[ \t]*\1)|(?:`[^`\n]+`)", re.MULTILINE | re.DOTALL)

# Repository whose "docs/" folder is the root of this website
ROOT_REPO = "rs-documentation"
ROOT_DOCS_DIR = "docs/"


def _site_path(repo: str, path: str) -> str:
    """Return the path, relative to the website docs_dir, of a file in the given repository."""
    if repo == ROOT_REPO:
        return path[len(ROOT_DOCS_DIR) :] if path.startswith(ROOT_DOCS_DIR) else ""
    return f"{repo}/{path}"


def _github_url(src_uri: str, docs_dir: str) -> str:
    """Return the GitHub URL of a file or folder given by its path relative to the website docs_dir."""
    repo, _, path = src_uri.partition("/")
    if not path or not os.path.exists(os.path.join(docs_dir, repo, ".git")):
        # File of the rs-documentation "docs/" folder itself (the other repositories are cloned under docs/)
        repo, path = ROOT_REPO, ROOT_DOCS_DIR + src_uri
    kind = "tree" if os.path.isdir(os.path.join(docs_dir, src_uri)) else "blob"
    return f"https://github.com/RS-PYTHON/{repo}/{kind}/develop/{path}"


def on_startup(command, dirty):  # pylint: disable=unused-argument
    """Called once when MkDocs starts."""
    # The docstring style warnings raised by griffe while generating the Python API documentation are code
    # quality issues, checked by the linters of each repository. Hide them so the documentation warnings
    # (e.g. broken links) are visible.
    for name in ("griffe", "mkdocs.plugins.griffe"):
        logging.getLogger(name).setLevel(logging.ERROR)


def on_page_markdown(markdown, page, config, files):  # pylint: disable=unused-argument
    """Rewrite the GitHub links of the page markdown before it is converted to HTML."""
    page_dir = posixpath.dirname(page.file.src_uri)

    def replace(match: re.Match) -> str:
        target = _site_path(match.group("repo"), match.group("path"))
        if not target or files.get_file_from_path(target) is None:
            return match.group(0)
        relative = posixpath.relpath(target, page_dir or ".")
        return relative + (match.group("anchor") or "")

    def replace_relative(match: re.Match) -> str:
        target, _, anchor = match.group("target").partition("#")
        src_uri = posixpath.normpath(posixpath.join(page_dir, target))
        file = files.get_file_from_path(src_uri)
        on_disk = os.path.exists(os.path.join(config["docs_dir"], src_uri))
        if src_uri.startswith("..") or not on_disk or (file is not None and not file.inclusion.is_excluded()):
            # Link to a page of the website, or broken link: let MkDocs validate it
            return match.group(0)
        url = _github_url(src_uri, config["docs_dir"]) + (f"#{anchor}" if anchor else "")
        return match.group("prefix") + url + match.group("suffix")

    def rewrite(text: str) -> str:
        return RELATIVE_LINK.sub(replace_relative, GITHUB_LINK.sub(replace, text))

    # Only rewrite the links outside the code blocks and code spans
    result = []
    position = 0
    for code in CODE.finditer(markdown):
        result.append(rewrite(markdown[position : code.start()]))
        result.append(code.group(0))
        position = code.end()
    result.append(rewrite(markdown[position:]))
    return "".join(result)
