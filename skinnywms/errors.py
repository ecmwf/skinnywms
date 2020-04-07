# (C) Copyright 2012-2019 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation nor
# does it submit to any jurisdiction.


__all__ = [
    "CurrentUpdateSequence",
    "GenericError",
    "InvalidCRS",
    "InvalidDimensionValue",
    "InvalidFormat",
    "InvalidPoint",
    "InvalidUpdateSequence",
    "LayerNotDefined",
    "LayerNotQueryable",
    "MissingDimensionValue",
    "OperationNotSupported",
    "ServiceNotDefined",
    "StyleNotDefined",
    "version_param",
    "wrap",
]


_TEMPLATE_1_1_1 = """
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE ServiceExceptionReport
  SYSTEM "http://schemas.opengis.net/wms/1.1.1/exception_1_1_1.dtd">
<ServiceExceptionReport version="1.1.1">
<ServiceException{code}><![CDATA[
{message}
]]>
</ServiceException>
</ServiceExceptionReport>
""".strip()

_TEMPLATE_1_3_0 = """
<?xml version='1.0' encoding="UTF-8"?>
<ServiceExceptionReport version="1.3.0"
  xmlns="http://www.opengis.net/ogc"
  xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
  xsi:schemaLocation="http://www.opengis.net/ogc http://schemas.opengis.net/wms/1.3.0/exceptions_1_3_0.xsd">
<ServiceException{code}><![CDATA[
{message}
]]>
</ServiceException>
</ServiceExceptionReport>
""".strip()


class WMSError(Exception):

    """Base class for WMS errors."""

    def __init__(self, message):
        super(WMSError, self).__init__(message)

    def body(self, version):
        """Return the response body for this WMS error.

        """
        if version == "1.1.1":
            template = _TEMPLATE_1_1_1
        else:
            template = _TEMPLATE_1_3_0

        code = self.code(version)
        if code is not None:
            code = ' code="{}"'.format(code)
        else:
            code = ""

        return template.format(code=code, message=self.message)

    def content_type(self, version):
        """Return the response content type for this WMS error.

        """
        if version == "1.1.1":
            return "application/vnd.ogc.se_xml"
        else:
            return "text/xml"

    def code(self, version):
        return self.__class__.__module__ + "." + self.__class__.__name__

    @property
    def message(self):
        return self.args[0]


class GenericError(WMSError):

    """Error with undefined code."""

    def code(self, version):
        return None


class CurrentUpdateSequence(WMSError):

    """Value of (optional) UpdateSequence parameter in GetCapabilities
    request is equal to current value of Capabilities XML update sequence
    number.

    """


class InvalidDimensionValue(WMSError):

    """Request contains an invalid sample dimension value."""


class InvalidFormat(WMSError):

    """Request contains a Format not offered by the service instance."""


class InvalidPoint(WMSError):

    """GetFeatureInfo request contains invalid point coordinates."""


class InvalidCRS(WMSError):

    """Request contains an CRS (or SRS, for WMS 1.1.1 requests) not
    offered by the service instance for one or more of the Layers in
    the request.

    """

    def code(self, version):
        if version == "1.1.1":
            return "InvalidSRS"
        else:
            return "InvalidCRS"


class InvalidUpdateSequence(WMSError):

    """Value of (optional) UpdateSequence parameter in GetCapabilities
    request is greater than current value of Capabilities XML update
    sequence number.

    """


class LayerNotDefined(WMSError):

    """Request is for a Layer not offered by the service instance."""


class LayerNotQueryable(WMSError):

    """GetFeatureInfo request is applied to a Layer which is not declared
    queryable.

    """


class MissingDimensionValue(WMSError):

    """Request does not include a sample dimension value, and the service
    instance did not declare a default value for that dimension.

    """


class OperationNotSupported(WMSError):

    """Request is for an optional operation that is not supported by the
    server.

    """


class ServiceNotDefined(WMSError):

    """The requested service is not available in this service instance.

    """


class StyleNotDefined(WMSError):

    """Request is for a Layer in a Style not offered by the service
    instance.

    """


def wrap(exc):
    """Ensure an error is an instance of `WMSError`.

    """
    if isinstance(exc, WMSError):
        return exc

    return WMSError(exc)


def version_param(params):
    """Return the value of the HTTP version parameter, or `None` if no
    version parameter is supplied.

    """
    for k, v in params.items():
        if k.lower() == "version":
            return v
