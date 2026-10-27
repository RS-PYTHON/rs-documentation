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

"""Thin layer on top of pyArchimate: refer to the elements by short keys and give stable identifiers to all the
concepts, so that a regenerated model can be re-imported into Enterprise Architect without duplicating it."""

import pyArchimate as pa  # pylint: disable=import-error
from pyArchimate.view import Point  # pylint: disable=import-error

# Colours of the nodes (the other ones keep the default ArchiMate colour of their layer)
EXTERNAL = "#E3E3E3"  # external systems
EXT_IFACE = "#FFB866"  # external interfaces of the System of Interest
SOI = "#7FD9F2"  # System of Interest (black box)
CONTAINER_APP = "#DDFBFB"
CONTAINER_TECH = "#E6F3DE"


class Builder:
    """A pyArchimate model whose concepts are referenced by short keys."""

    def __init__(self, name: str, doc: str):
        self.model = pa.Model(name)
        self.model.desc = doc
        self.elements: dict = {}
        self.rels: dict = {}

    def el(self, key: str, etype: str, name: str, doc: str = "", **props):
        """Add an element, identified by "id-<key>"."""
        e = self.model.add(concept_type=etype, name=name, uuid=f"id-{key}", desc=doc or None)
        for k, v in props.items():
            e.prop(k, v)
        self.elements[key] = e
        return e

    def rel(self, rtype: str, source: str, target: str, name: str = "", access: str | None = None):
        """Add a relationship (or return the identical existing one); raise if ArchiMate does not allow it."""
        signature = (rtype, source, target, name, access)
        if signature not in self.rels:
            src, tgt = self.elements[source], self.elements[target]
            pa.check_valid_relationship(rtype, src.type, tgt.type, raise_flg=True)
            self.rels[signature] = self.model.add_relationship(
                rel_type=rtype,
                source=src,
                target=tgt,
                uuid=f"id-r{len(self.rels) + 1:03d}",
                name=name or None,
                access_type=access,
            )
        return self.rels[signature]

    def view(self, key: str, name: str, viewpoint: str, doc: str) -> "ViewBuilder":
        """Add a view, identified by "id-view-<key>"."""
        return ViewBuilder(self, key, name, viewpoint, doc)


class ViewBuilder:
    """A pyArchimate view whose nodes are referenced by the keys of their elements."""

    def __init__(self, builder: Builder, key: str, name: str, viewpoint: str, doc: str):
        self.builder = builder
        self.key = key
        # Viewpoint of the Open Group standard, in the documentation: pyArchimate only knows its own viewpoint slugs,
        # and does not write the definitions of the view properties
        desc = f"{doc} ArchiMate viewpoint: {viewpoint}."
        self.view = builder.model.add(concept_type=pa.ArchiType.View, name=name, uuid=f"id-view-{key}", desc=desc)
        self.by_element: dict = {}
        self.notes = 0

    def add(self, element: str, x: int, y: int, w: int, h: int, **opts):
        """Add a node, with the options parent, nest (relationship backing the nesting, Composition by default),
        fill and font_size."""
        parent_key = opts.get("parent")
        parent = self.by_element[parent_key] if parent_key else self.view
        node = parent.add(self.builder.elements[element], x, y, w, h, uuid=f"id-{self.key}-{element}")
        if parent_key and opts.get("nest", "Composition"):
            self.builder.rel(opts.get("nest", "Composition"), parent_key, element)
        if opts.get("fill"):
            node.fill_color = opts["fill"]
        if opts.get("font_size"):
            node.font_size = opts["font_size"]
        self.by_element[element] = node
        return node

    def note(self, text: str, x: int, y: int, w: int, h: int, **opts):
        """Add a note, with the option parent."""
        self.notes += 1
        owner = self.by_element[opts["parent"]] if opts.get("parent") else self.view
        return owner.add(None, x, y, w, h, uuid=f"id-{self.key}-note{self.notes}", node_type="Label", label=text)

    def connect(self, rtype: str, source: str, target: str, name: str = "", **opts):
        """Draw a relationship (created if needed), with the options bend (list of bendpoints) and access."""
        rel = self.builder.rel(rtype, source, target, name, opts.get("access"))
        conn = self.view.add_connection(
            rel,
            self.by_element[source],
            self.by_element[target],
            uuid=f"id-{self.key}-c{len(self.view.conns) + 1}",
        )
        for x, y in opts.get("bend", ()):
            conn.add_bendpoint(Point(x, y))
        return conn

    def flow(self, source: str, target: str, name: str = "", **opts):
        """Draw a flow relationship."""
        return self.connect("Flow", source, target, name, **opts)

    def serve(self, source: str, target: str, name: str = "", **opts):
        """Draw a serving relationship."""
        return self.connect("Serving", source, target, name, **opts)
