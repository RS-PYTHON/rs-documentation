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

"""MkDocs hook that removes the boilerplate of the Markdown pages, repeated in all the repositories.

The Markdown files are written to be read both on GitHub and in this website. Some of their content is useful on
GitHub, where each file is read on its own, but only makes the website heavier:

- The README of each RS-PYTHON repository ends with the same "Contributing" and "Licensing" sections (followed by
  the funding banner). In the website, they would be repeated on almost every page, while the same information is
  already given once in the home page and in the contribution guidelines.
- The code examples are often copied from source files, with their license header. It makes the examples longer
  without being useful to the reader.
"""

import os
import re

# Titles of the level 2 sections removed from the repository READMEs
REMOVED_SECTIONS = {"contributing", "licensing"}

# Markdown ATX heading: level and title
HEADING = re.compile(r"^(?P<level>#{1,6})\s+(?P<title>.*?)\s*#*\s*$")

# Start or end of a fenced code block, with its indentation (e.g. inside a list item)
FENCE = re.compile(r"^(?P<indent>[ \t]*)(?P<fence>`{3,}|~{3,})")

# Comment line of a code block: '#' (shell, YAML, Python...), '//' (JS, Go...), '--' (SQL), ';' (INI)
LINE_COMMENT = re.compile(r"^\s*(#|//|--|;)")

# Block comment, as one string: <!-- ... --> (HTML, XML) or /* ... */ (CSS, Java...)
BLOCK_COMMENT = re.compile(r"^\s*(<!--.*?-->|/\*.*?\*/)\s*\n?", re.DOTALL)

# Last line of the Apache license header
LICENSE_END = "limitations under the License."


def _is_repository_readme(src_uri: str, docs_dir: str) -> bool:
    """Return True if the page is the README at the root of a repository cloned under docs_dir."""
    repo, _, path = src_uri.partition("/")
    return path == "README.md" and os.path.exists(os.path.join(docs_dir, repo, ".git"))


def _is_license_header(comment: str) -> bool:
    """Return True if the comment is a license header."""
    return "Copyright" in comment and "License" in comment


def remove_sections(markdown: str, titles: set[str]) -> str:
    """Remove the level 2 sections with the given titles (case-insensitive), up to the next level 1 or 2 heading."""
    result = []
    removing = False
    fence = None
    for line in markdown.splitlines(keepends=True):
        match = FENCE.match(line)
        if fence is None and match:
            fence = match.group("fence")
        elif fence is not None:
            if match and match.group("fence") == fence:
                fence = None
        elif heading := HEADING.match(line):
            if len(heading.group("level")) <= 2:
                removing = len(heading.group("level")) == 2 and heading.group("title").lower() in titles
        if not removing:
            result.append(line)
    return "".join(result).rstrip() + "\n"


def remove_code_license_header(code: str) -> str:
    """Remove the license header at the start of a code block, and the blank lines that follow it.

    The header is kept if the code block contains nothing else: it is then an example of license header.
    """
    lines = code.splitlines(keepends=True)
    start = next((i for i, line in enumerate(lines) if line.strip()), len(lines))
    # Keep the shebang line, e.g. '#!/bin/bash'
    shebang = lines[start] if start < len(lines) and lines[start].lstrip().startswith("#!") else ""
    if shebang:
        start += 1
    if block := BLOCK_COMMENT.match("".join(lines[start:])):
        header, rest = block.group(0), "".join(lines[start:])[block.end() :]
    else:
        end = start
        while end < len(lines) and LINE_COMMENT.match(lines[end]):
            end += 1
            # End of the Apache license header: the next comments are part of the example
            if LICENSE_END in lines[end - 1]:
                break
        header, rest = "".join(lines[start:end]), "".join(lines[end:])
    if not _is_license_header(header) or not rest.strip():
        return code
    return shebang + rest.lstrip("\n")


def remove_code_license_headers(markdown: str) -> str:
    """Remove the license header at the start of the fenced code blocks of the page."""
    result = []
    code: list[str] = []
    fence = None
    for line in markdown.splitlines(keepends=True):
        match = FENCE.match(line)
        if fence is None:
            result.append(line)
            if match:
                fence = match.group("indent") + match.group("fence")
        elif line.lstrip(" \t").startswith(fence.lstrip(" \t")) and not line.strip().strip(fence[-1]):
            result.append(remove_code_license_header("".join(code)))
            result.append(line)
            code, fence = [], None
        else:
            code.append(line)
    # Unclosed code block: keep it unchanged
    result.extend(code)
    return "".join(result)


def on_page_markdown(markdown, page, config, files):  # pylint: disable=unused-argument
    """Remove the boilerplate of the page markdown before it is converted to HTML."""
    if _is_repository_readme(page.file.src_uri, config["docs_dir"]):
        markdown = remove_sections(markdown, REMOVED_SECTIONS)
    return remove_code_license_headers(markdown)
