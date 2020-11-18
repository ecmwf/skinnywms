# (C) Copyright 2012-2019 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation nor
# does it submit to any jurisdiction.

import logging
import os
import tempfile


from skinnywms import errors, protocol

LOG = logging.getLogger(__name__)


def revert_bbox(bbox):
    minx, miny, maxx, maxy = bbox
    return [miny, minx, maxy, maxx]


bounding_box = {"1.3.0_EPSG:4326": revert_bbox}


class TmpFile:
    def __init__(self):
        self.fname = None

    def target(self, ext):
        fd, self.fname = tempfile.mkstemp(
            prefix="wms-server-", suffix=".{}".format(ext)
        )
        os.close(fd)

        # Change output plot file permissions to something more reasonable, so
        # we are at least able to read the produced plots if directed outside
        # the docker environment (through the use of --volume).
        os.chmod(self.fname, 0o644)
        return self.fname

    def content(self):
        with open(self.fname, "rb") as f:
            c = f.read()
            os.close(f)
        return c

    def cleanup(self):
        LOG.debug("Deleting %s" % self.fname)
        os.unlink(self.fname)


class NoCaching:
    def create_output(self):
        return TmpFile()


class WMSServer:
    def __init__(self, availability, plotter, styler, caching=NoCaching()):

        self.availability = availability
        self.availability.set_context(self)

        self.plotter = plotter
        self.plotter.set_context(self)

        self.styler = styler
        self.styler.set_context(self)

        self.caching = caching

        # For objects to store context
        self.stash = {}

    def process(
        self, request, Response, send_file, render_template, reraise=False, output=None
    ):

        url = request.url.split("?")[0]

        LOG.info(request.url)

        params, _ = protocol.filter_wms_params(request.args)

        service_orig = params.setdefault("service", "wms")
        service = service_orig.lower()

        version = params.setdefault("version", "1.3.0")

        req_orig = params.setdefault("request", "getcapabilities")
        req = req_orig.lower()

        if output is None:
            output = self.caching.create_output()

        try:
            LOG.info(req)
            if service != "wms":
                raise errors.ServiceNotDefined(service_orig)

            if version not in protocol.SUPPORTED_VERSIONS:
                raise Exception("Unsupported WMS version {}".format(version))

            if req == "getcapabilities":
                content_type, content = self.get_capabilities(
                    version, url, render_template
                )
            elif req == "getmap":
                params = protocol.get_wms_parameters(req, version, params)
                params["_macro"] = request.args.get("_macro", False)
                params["output"] = output

                for k in ("request", "service"):
                    try:
                        del params[k]
                    except KeyError:
                        pass
                if version == "1.1.1":
                    srs = params.pop("srs")
                    params["crs"] = srs

                content_type, path = self.get_map(**params)
                resp = send_file(path, content_type)
                output.cleanup()

                return resp

            elif req == "getlegendgraphic":
                params = protocol.get_wms_parameters(req, version, params)

                params["output"] = output

                for k in ("request", "service"):
                    try:
                        del params[k]
                    except KeyError:
                        pass

                content_type, path = self.get_legend(**params)
                resp = send_file(path, content_type)
                output.cleanup()

                return resp

            else:
                raise errors.OperationNotSupported(req_orig)
        except errors.WMSError as exc:
            if reraise:
                raise
            LOG.exception("%s(): Error: %s", req, exc)
            content_type = exc.content_type(version)
            content = exc.body(version)

        except Exception as exc:
            if reraise:
                raise

            LOG.exception("%s(): Error: %s", req, exc)
            exc = errors.wrap(exc)
            content_type = exc.content_type(version)
            content = exc.body(version)

        return Response(content, mimetype=content_type)

    def get_map(
        self,
        output,
        bbox,
        crs,
        format,
        height,
        layers,
        version,
        width,
        styles=None,
        _macro=False,
        bgcolor=None,
        dim_index=None,
        elevation=None,
        exceptions=None,
        time=None,
        transparent=True,
    ):

        if not styles:
            styles = []

        while len(styles) < len(layers):
            styles.append("")

        # collect the dims, the fields selection is based on this information
        dims = {"time": time, "elevation": elevation, "dim_index": dim_index}

        layer_objs = []
        for name in layers:
            try:
                layer = self.availability.layer(name, dims)
            except errors.LayerNotDefined:
                layer = self.plotter.layer(name)

            layer_objs.append(layer)

        # Interpret the BBox

        bbox = bounding_box.get("{}_{}".format(version, crs), (lambda x: x))(bbox)

        LOG.debug("->{}_{}".format(version, crs))

        mime_type, path = self.plotter.plot(
            self,
            output,
            bbox,
            crs,
            format,
            height,
            layer_objs,
            styles,
            version,
            width,
            _macro=_macro,
            bgcolor=bgcolor,
            elevation=elevation,
            exceptions=exceptions,
            time=time,
            transparent=transparent,
        )

        return mime_type, path

    def get_legend(
        self,
        output,
        layer,
        version,
        format="image/png",
        style="",
        height=150,
        width=600,
        exceptions=None,
        transparent=True,
    ):

        time = None

        try:
            legend = self.availability.layer(layer, time)
        except errors.LayerNotDefined:
            legend = self.plotter.layer

        path = self.plotter.legend(
            self, output, format, height, legend, style, version, width, transparent,
        )

        return format, path

    def get_capabilities(self, version, service_url, render_template):

        layers = list(self.availability.layers())
        LOG.info("Layers are %s", layers)

        if self.availability.auto_add_plotter_layers:
            layers += list(self.plotter.layers())

        layers = sorted(layers, key=lambda k: k.zindex)

        LOG.info("LAYERS are %r", layers)

        variables = {
            "service": {"title": "WMS", "url": service_url,},
            "crss": self.plotter.supported_crss,
            "geographic_bounding_box": self.plotter.geographic_bounding_box,
            "layers": layers,
        }

        content_type = "text/xml"
        content = render_template("getcapabilities_{}.xml".format(version), **variables)
        return content_type, content
