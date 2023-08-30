# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

from lxml import etree


def set_background_color(diagram: bytes, backgroundcolor: str) -> bytes:
    tree = etree.fromstring(diagram)
    first_elem = tree[0]
    if first_elem.tag == "{http://www.w3.org/2000/svg}rect":
        first_elem.attrib["fill"] = backgroundcolor
    else:
        background_elem = etree.Element(
            "rect",
            x="0",
            y="0",
            width="100%",
            height="100%",
            fill=backgroundcolor,
        )
        tree.insert(0, background_elem)
    return etree.tostring(tree)
