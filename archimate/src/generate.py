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

"""Generate the RS-Python ArchiMate model with pyArchimate: Open Group exchange format, SVG previews (and PNG
previews when resvg_py is installed) and table of the functional packages, in the archimate folder.

Usage: python3 generate.py (the Open Group XSD files must be in the archimate/xsd folder, see the README)
"""

import importlib
import sys
from pathlib import Path

import pyArchimate as pa  # pylint: disable=import-error
from lxml import etree  # pylint: disable=import-error
from pyArchimate.view.layout import export  # pylint: disable=import-error
from rs_python_elements import FUNCTIONAL_PACKAGES
from rs_python_model import build

LICENSE_HEADER = """
  Copyright 2023-2026 Airbus, CS Group

  Licensed under the Apache License, Version 2.0 (the "License");
  you may not use this file except in compliance with the License.
  You may obtain a copy of the License at

      http://www.apache.org/licenses/LICENSE-2.0

  Unless required by applicable law or agreed to in writing, software
  distributed under the License is distributed on an "AS IS" BASIS,
  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
  See the License for the specific language governing permissions and
  limitations under the License.
"""

# Output folder, and folder of the Open Group ArchiMate 3.1 XSD files
ARCHIMATE_DIR = Path(__file__).resolve().parent.parent
XSD_DIR = ARCHIMATE_DIR / "xsd"

# Parser of the generated and XSD files: no entity resolution, no network access
PARSER = etree.XMLParser(resolve_entities=False, no_network=True, remove_blank_text=True)


class FixedSVGExport(export.SVGExportService):  # pylint: disable=too-few-public-methods
    """pyArchimate SVG export, with workarounds:

    - label the relationships with their names (e.g. the data of the flows) instead of their types, which are
      already given by the notation,
    - start the view box at the origin: pyArchimate draws the white background from the origin, while its view box
      starts at a negative margin, which leaves a transparent band at the top and on the left,
    - keep the line breaks of the texts (e.g. the lists in the notes), that pyArchimate merges into a single paragraph.
    """

    def _build_relationship_label(self, rel_type: str, conn) -> str:  # pylint: disable=unused-argument
        return conn.name or ""

    def _word_wrap_text(self, text: str, max_width: float) -> list[str]:
        return [line for paragraph in text.split("\n") for line in super()._word_wrap_text(paragraph, max_width)]

    def _calculate_bounds(self, view) -> dict[str, float]:
        bounds = super()._calculate_bounds(view)
        bounds["min_x"] = bounds["min_y"] = 0.0
        return bounds


def check(model):
    """Check the model with pyArchimate: relationships allowed by ArchiMate, valid nodes and connections."""
    errors = {
        "invalid relationships": model.check_invalid_relationships(),
        "invalid connections": model.check_invalid_conn(),
        "invalid nodes": model.check_invalid_nodes(),
    }
    for kind, ids in errors.items():
        if ids:
            print(f"{kind}: {ids}")
            sys.exit(1)


def write_xml(model, xml_path: Path, xsd_dir: Path):
    """Write the model in the Open Group exchange format, with the license header, and validate it."""
    root = etree.fromstring(model.write(writer=pa.Writers.archimate).encode(), PARSER)
    etree.indent(root, space="  ")
    body = etree.tostring(root, encoding="unicode")
    xml_path.write_text(f'<?xml version="1.0" encoding="UTF-8"?>\n<!--{LICENSE_HEADER}-->\n{body}\n', encoding="utf-8")
    schema = etree.XMLSchema(etree.parse(str(xsd_dir / "archimate3_Diagram.xsd"), PARSER))
    if not schema.validate(etree.parse(str(xml_path), PARSER)):
        print(schema.error_log)
        sys.exit(1)
    print(f"{xml_path.name}: valid against the ArchiMate 3.1 exchange format schema")


def previews(model, out: Path):
    """SVG previews of the views, and PNG ones if resvg_py is installed."""
    out.mkdir(exist_ok=True)
    try:
        resvg = importlib.import_module("resvg_py")
    except ImportError:
        resvg = None
    for view in model.views:
        svg = out / f"{view.name.split(' ', 1)[0].rstrip('.')}-{view.uuid.removeprefix('id-view-')}.svg"
        svg.write_text(f'<?xml version="1.0" encoding="UTF-8"?>\n{FixedSVGExport().to_svg(view)}\n', encoding="utf-8")
        if resvg:
            png = resvg.svg_to_bytes(svg_path=str(svg), sans_serif_family="DejaVu Sans")
            svg.with_suffix(".png").write_bytes(bytes(png))
        print(f"preview: {svg.name}")


def functional_table(builder, out: Path):
    """Markdown table of the functional packages."""
    lines = [
        "# RS-Python - Functional packages",
        "",
        "| Functional package | Description | Functions | Supported services | Components |",
        "|---|---|---|---|---|",
    ]
    for package in FUNCTIONAL_PACKAGES:
        functions = "<br>".join(f for f, _ in package.functions)
        services = "<br>".join(builder.elements[s].name for s in package.services)
        lines.append(
            f"| **{package.name}** | {package.description} | {functions} | {services} | {package.components} |",
        )
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    """Command line entry point."""
    if not (XSD_DIR / "archimate3_Diagram.xsd").is_file():
        print(f"Download the Open Group XSD files into {XSD_DIR} first, see the README")
        sys.exit(1)
    builder = build()
    check(builder.model)
    write_xml(builder.model, ARCHIMATE_DIR / "rs-python-architecture.xml", XSD_DIR)
    print(f"{len(builder.elements)} elements, {len(builder.rels)} relationships, {len(builder.model.views)} views")
    previews(builder.model, ARCHIMATE_DIR / "previews")
    functional_table(builder, ARCHIMATE_DIR / "functional-packages.md")


if __name__ == "__main__":
    main()
