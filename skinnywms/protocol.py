# (C) Copyright 2012-2019 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation nor
# does it submit to any jurisdiction.

__all__ = [
    "SUPPORTED_VERSIONS",
    "filter_wms_params",
    "get_wms_parameters",
]

# Supprted WMS versions in this implementation.
SUPPORTED_VERSIONS = frozenset(("1.1.1", "1.3.0"))


def _bbox_norm(v):
    min_x, min_y, max_x, max_y = [float(f) for f in v.split(",")]
    if min_x >= max_x:
        raise ValueError(
            "Invalid combination of min_x={} and max_x={}".format(min_x, max_x)
        )
    if min_y >= max_y:
        raise ValueError(
            "Invalid combination of min_y={} and max_y={}".format(min_y, max_y)
        )
    return min_x, min_y, max_x, max_y


def _transparent_norm(v):
    v = v.upper()
    if v == "TRUE":
        return True
    if v == "FALSE":
        return False
    raise ValueError("Expected 'TRUE' or 'FALSE'")


# Known HTTP query parameters for WMS.
#
# From:
#
#     * [WMS 1.1.1](http://portal.opengeospatial.org/files/?artifact_id=1081)
#     * [WMS 1.3.0](http://portal.opengeospatial.org/files/?artifact_id=14416)
#
# Anything starting with `dim_` is also a WMS parameter.
_WMS_KNOWN_PARAMS = {
    ("getcapabilities", "1.1.1"): (
        ("format", False, None),
        ("request", True, None),
        ("service", True, None),
        ("updatesequence", False, None),
        ("version", False, None),
    ),
    ("getcapabilities", "1.3.0"): (
        ("format", False, None),
        ("request", True, None),
        ("service", True, None),
        ("updatesequence", False, None),
        ("version", False, None),
    ),
    ("getmap", "1.1.1"): (
        ("bbox", True, _bbox_norm),
        ("bgcolor", False, None),
        ("srs", True, None),
        ("elevation", False, None),
        ("exceptions", False, None),
        ("format", True, None),
        ("height", True, int),
        ("layers", True, lambda v: v.split(",")),
        ("request", True, None),
        ("styles", False, lambda v: v.split(",")),
        ("time", False, None),
        ("transparent", False, _transparent_norm),
        ("version", True, None),
        ("width", True, int),
    ),
    ("getmap", "1.3.0"): (
        ("bbox", True, _bbox_norm),
        ("bgcolor", False, None),
        ("crs", True, None),
        ("dim_index", False, None),
        ("elevation", False, None),
        ("exceptions", False, None),
        ("format", True, None),
        ("height", True, int),
        ("layers", True, lambda v: v.split(",")),
        ("request", True, None),
        ("styles", False, lambda v: v.split(",")),
        ("time", False, None),
        ("transparent", False, _transparent_norm),
        ("version", True, None),
        ("width", True, int),
    ),
    ("getlegendgraphic", "1.1.1"): (
        ("exceptions", False, None),
        ("format", False, None),
        ("height", False, int),
        ("layer", True, None),
        ("request", True, None),
        ("style", False, None),
        ("version", False, None),
        ("width", False, int),
        ("transparent", False, _transparent_norm),
    ),
    ("getlegendgraphic", "1.3.0"): (
        ("exceptions", False, None),
        ("format", False, None),
        ("height", False, int),
        ("layer", True, None),
        ("request", True, None),
        ("style", False, None),
        ("version", False, None),
        ("width", False, int),
        ("transparent", False, _transparent_norm),
    ),
}

_WMS_QUERY_PARAMS = []
for params in _WMS_KNOWN_PARAMS.values():
    _WMS_QUERY_PARAMS.extend(name for (name, _, _) in params)
_WMS_QUERY_PARAMS = frozenset(_WMS_QUERY_PARAMS)


def filter_wms_params(params):
    """Split a dict of HTTP request parameters in WMS-specific and
    non-WMS-specific parameters.

    Keys in the returned dicts are always lower-case. Values are left
    untouched.

        >>> wms, non_wms = filter_wms_params({'Service': 'WMS', 'FOO': 'Bar'})
        >>> wms
        {'service': 'WMS'}
        >>> non_wms
        {'foo': 'Bar'}

    Either of both dictionaries might be empty.

    """
    wms = {}
    non_wms = {}
    for k, v in params.items():
        k = k.lower()
        if k in _WMS_QUERY_PARAMS:
            wms[k] = v
        else:
            non_wms[k] = v
    return wms, non_wms


def get_wms_parameters(request, version, params):
    ret = {}
    for k, required, norm in _WMS_KNOWN_PARAMS[(request, version)]:
        try:
            v = params[k]
        except KeyError:
            if required:
                raise ValueError("Missing parameter '{}".format(k))
        else:
            if callable(norm):
                try:
                    v = norm(v)
                except Exception as exc:
                    raise ValueError(
                        "Invalid value '{}' for parameter '{}': {}".format(v, k, exc)
                    )
            ret[k] = v
    return ret
