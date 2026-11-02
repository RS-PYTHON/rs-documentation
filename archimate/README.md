# RS-Python - ArchiMate architecture diagrams

ArchiMate 3.2 model of RS-Python, with the six views of the Architecture Dossier. This folder is outside the `docs`
folder: it is not part of the HTML documentation.

| File | Content |
|---|---|
| `rs-python-architecture.xml` | The whole model (elements, relationships, views) in **The Open Group ArchiMate Model Exchange File Format** (schema 3.1). |
| `functional-packages.md` | Table of the functional packages (description, functions, supported services, allocated components). |
| `previews/*.svg`, `previews/*.png` | Previews of the views (white background for the SVG, transparent for the PNG), for review only: the reference rendering is the one of the modelling tool. |
| `src/` | Python generator of all the files above. |

Views:

1. System in Context
2. Functional Top-Level Decomposition
3. High Level Application View
4. Detailed Application View
5. Infrastructure Logical View
6. Network View

## Open the model

- **Sparx Enterprise Architect**: select a package, then *Specialize > Technologies > ArchiMate > Import Model
  Exchange File* and choose `rs-python-architecture.xml`. EA creates the elements, the relationships, the folders
  (Business, Application, Technology & Physical, Other, Relations, Views) and the six diagrams with their layout,
  colours and notes.
- **Archi**: *File > Import > Open Exchange XML Model*.

## Conventions

- Dark blue: the System of Interest (black box) in the context view.
- Orange: external interfaces of RS-Python. Grey: external systems.
- Nesting always stands for a relationship of the model (composition, aggregation, assignment or realization), as
  allowed by the ArchiMate 3.2 specification.
- Network zones are groupings; networks are communication networks.

## Regenerate

The model is built with [pyArchimate](https://github.com/pyArchimate/pyArchimate) (GPL-3.0, used as a tool only:
it is not distributed with RS-Python), which also checks the relationships against the ArchiMate 3.2 rules, writes
the exchange format and renders the SVG previews. The output is validated against the Open Group XSD files.

```shell
pip install pyArchimate==2.0.2 lxml resvg-py  # resvg-py is optional: without it, only the SVG previews are generated

# Open Group XSD files, in the archimate/xsd folder (ignored by git)
mkdir -p archimate/xsd && cd archimate/xsd
for f in archimate3_Model.xsd archimate3_View.xsd archimate3_Diagram.xsd; do
    curl -sO https://www.opengroup.org/xsd/archimate/3.1/$f
done
curl -sO https://www.w3.org/2001/xml.xsd
sed -i 's#schemaLocation="http://www.w3.org/2001/xml.xsd"#schemaLocation="xml.xsd"#' archimate3_Model.xsd
cd -

python archimate/src/generate.py
```

| Source | Content |
|---|---|
| `src/rs_python_elements.py` | Elements and functional packages. |
| `src/rs_python_views.py` | Content and layout of the six views. |
| `src/rs_python_model.py` | Assembly of the model. |
| `src/model_builder.py` | Thin layer on top of pyArchimate: short keys and stable identifiers, so that a regenerated model can be re-imported into EA without duplicating it. |
| `src/generate.py` | Checks, export, previews (see the rendering choices below). |

Rendering choices of the previews, on top of the pyArchimate SVG export:

- The relationships are only labelled with their names (data of the flows, protocols...): pyArchimate labels the
  unnamed ones with their types, which are already given by the notation.
- The PNG previews are transparent: the white background of the SVG export is left out. To keep them readable on
  light and dark backgrounds, the groupings drawn on the canvas get a white background, and the relationships and
  arrowheads a white halo.
