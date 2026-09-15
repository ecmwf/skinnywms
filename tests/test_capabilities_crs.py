# (C) Copyright 2012-2019 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation nor
# does it submit to any jurisdiction.

"""Check the CRS section of the GetCapabilities documents.

WMS 1.3.0 uses the latitude/longitude axis order for EPSG:4326 only; every
other CRS, in particular the projected ones (EPSG:3857, ESRI:54035, ...), uses
the x/y (easting/northing) order. WMS 1.1.1 always uses the x/y order.
"""

import os
import re

import jinja2

import skinnywms
from skinnywms.datatypes import CRS
from skinnywms.server import WMSServer

TEMPLATES = os.path.join(os.path.dirname(skinnywms.__file__), "templates")

GEOGRAPHIC = CRS("EPSG:4326", n_lat=90.0, s_lat=-90.0, w_lon=-180.0, e_lon=180.0)
EQUAL_EARTH = CRS(
    "ESRI:54035",
    n_lat=8392927.60,
    s_lat=-8392927.60,
    w_lon=-17243959.06,
    e_lon=17243959.06,
)


class FakeAvailability:
    auto_add_plotter_layers = False

    def set_context(self, context):
        pass

    def layers(self):
        return []


class FakePlotter:
    def __init__(self, crss):
        self._crss = tuple(crss)

    def set_context(self, context):
        pass

    @property
    def supported_crss(self):
        return self._crss

    @property
    def geographic_bounding_box(self):
        return {"w_lon": -180.0, "e_lon": 180.0, "s_lat": -90.0, "n_lat": 90.0}

    def layers(self):
        return []


class FakeStyler:
    def set_context(self, context):
        pass


def render_template(name, **variables):
    env = jinja2.Environment(loader=jinja2.FileSystemLoader(TEMPLATES))
    return env.get_template(name).render(**variables)


def capabilities(version):
    server = WMSServer(
        FakeAvailability(), FakePlotter([GEOGRAPHIC, EQUAL_EARTH]), FakeStyler()
    )
    content_type, content = server.get_capabilities(
        version, "http://localhost/wms", render_template
    )
    assert content_type == "text/xml"
    return content


def bounding_boxes(xml):
    pattern = (
        r'<BoundingBox CRS="([^"]+)" minx="([^"]+)" miny="([^"]+)"'
        r' maxx="([^"]+)" maxy="([^"]+)"'
    )
    return {
        m.group(1): tuple(float(m.group(i)) for i in range(2, 6))
        for m in re.finditer(pattern, xml)
    }


def test_crs_advertised():
    for version in ("1.1.1", "1.3.0"):
        xml = capabilities(version)
        assert "<CRS>EPSG:4326</CRS>" in xml
        assert "<CRS>ESRI:54035</CRS>" in xml


def test_bounding_box_axis_order_1_3_0():
    boxes = bounding_boxes(capabilities("1.3.0"))
    # latitude/longitude order for EPSG:4326
    assert boxes["EPSG:4326"] == (-90.0, -180.0, 90.0, 180.0)
    # x/y order for projected CRSs
    assert boxes["ESRI:54035"] == (
        -17243959.06,
        -8392927.60,
        17243959.06,
        8392927.60,
    )


def test_bounding_box_axis_order_1_1_1():
    boxes = bounding_boxes(capabilities("1.1.1"))
    assert boxes["EPSG:4326"] == (-180.0, -90.0, 180.0, 90.0)
    assert boxes["ESRI:54035"] == (
        -17243959.06,
        -8392927.60,
        17243959.06,
        8392927.60,
    )
