# (C) Copyright 2012-2019 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation nor
# does it submit to any jurisdiction.

"""Tests that public URLs in responses honour X-Forwarded-* headers, if and
only if SKINNYWMS_TRUST_XFORWARDED is enabled."""

import re

import pytest

from skinnywms import wmssvr
from skinnywms.server import BASE_URL_PLACEHOLDER, _escape_attr_content

FORWARDED = {
    "X-Forwarded-Proto": "https",
    "X-Forwarded-Host": "example.com:8443",
    "X-Forwarded-Prefix": "/api/proxy/abc",
}
PUBLIC = "https://example.com:8443/api/proxy/abc"


@pytest.fixture
def make_client():
    """Yields a factory for test clients, with the app restored afterwards."""
    original = wmssvr.application.wsgi_app

    def factory(trust):
        wmssvr.application.wsgi_app = original
        if trust:
            wmssvr._enable_proxy_fix()
        return wmssvr.application.test_client()

    yield factory
    wmssvr.application.wsgi_app = original


def hrefs(body):
    return re.findall(r'xlink:href="([^"]*)"', body)


def service_hrefs(body):
    return [h for h in hrefs(body) if "/wms" in h and "schemas" not in h]


def capabilities(client, version, headers=None):
    resp = client.get(
        f"/wms?request=GetCapabilities&service=WMS&version={version}",
        headers=headers or {},
    )
    assert resp.status_code == 200
    return resp.get_data(as_text=True)


@pytest.mark.parametrize("version", ["1.1.1", "1.3.0"])
def test_trusted_headers_are_used(make_client, version):
    body = capabilities(make_client(True), version, FORWARDED)
    found = service_hrefs(body)
    assert len(found) >= 3
    assert all(h.startswith(PUBLIC + "/wms") for h in found), found
    assert BASE_URL_PLACEHOLDER not in body
    assert "127.0.0.1" not in "".join(found)


@pytest.mark.parametrize("version", ["1.1.1", "1.3.0"])
def test_headers_ignored_by_default(make_client, version):
    body = capabilities(make_client(False), version, FORWARDED)
    found = service_hrefs(body)
    assert found
    assert all(h.startswith("http://localhost/wms") for h in found), found
    assert "example.com" not in body


def test_trusted_without_headers_falls_back_to_request(make_client):
    body = capabilities(make_client(True), "1.3.0")
    assert all(h.startswith("http://localhost/wms") for h in service_hrefs(body))


def test_cache_is_independent_of_host(make_client):
    client = make_client(True)
    capabilities(client, "1.3.0", FORWARDED)
    capabilities(client, "1.3.0", {"X-Forwarded-Host": "other.org"})
    capabilities(client, "1.3.0", {"Host": "yet.another"})
    cache = wmssvr.server._capabilities_cache
    assert {k[0] for k in cache} <= {"1.1.1", "1.3.0"}
    assert len(cache) <= 2
    assert all(BASE_URL_PLACEHOLDER in v for v in cache.values())
    body = capabilities(client, "1.3.0", FORWARDED)
    assert all(h.startswith(PUBLIC + "/wms") for h in service_hrefs(body))


def test_hostile_host_is_escaped(make_client):
    body = capabilities(make_client(True), "1.3.0", {"X-Forwarded-Prefix": "/a><b&"})
    assert "/a><b&" not in body
    assert "/a&gt;&lt;b&amp;/wms" in body


def test_escape_attr_content():
    assert _escape_attr_content('a"<&>') == "a&quot;&lt;&amp;&gt;"


def test_legend_url_uses_public_base(make_client):
    body = capabilities(make_client(True), "1.3.0", FORWARDED)
    legends = [h for h in hrefs(body) if "GetLegendGraphic" in h]
    if legends:
        assert all(h.startswith(PUBLIC + "/wms?request=") for h in legends)


def test_demo_page_urls(make_client):
    page = make_client(True).get("/", headers=FORWARDED).get_data(as_text=True)
    assert 'const WMS_URL = "/api/proxy/abc/wms"' in page
    assert "/api/proxy/abc/static/js/leaflet-1.3.1.js" in page
    page = make_client(False).get("/").get_data(as_text=True)
    assert 'const WMS_URL = "/wms"' in page
    assert 'src="/static/js/leaflet-1.3.1.js"' in page


def test_proxy_fix_not_applied_twice(make_client):
    make_client(True)
    inner = wmssvr.application.wsgi_app
    wmssvr._enable_proxy_fix()
    assert wmssvr.application.wsgi_app is inner
