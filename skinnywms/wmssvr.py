# (C) Copyright 2012-2019 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation nor
# does it submit to any jurisdiction.

import argparse
import logging
import os

from . import __version__
from flask import (
    Flask,
    Response,
    abort,
    jsonify,
    render_template,
    request,
    send_file,
    send_from_directory,
)
from flask_cors import CORS

from .data.fs import Availability
from .plot.magics import Plotter, Styler
from .server import WMSServer

logging.basicConfig(level=os.environ.get("LOGLEVEL", "WARN"))
LOG = logging.getLogger(__name__)

application = Flask(__name__, static_url_path="/static", static_folder=None)

demo = os.path.join(os.path.dirname(__file__), "testdata")
package_static = os.path.join(os.path.dirname(__file__), "static")


def _env_data_path():
    path = os.environ.get("SKINNYWMS_DATA_PATH", "")
    return path if path != "" else demo


def _env_bool(name):
    value = os.environ.get(name, "")
    return value != "" and value == "1"


def _env_origins():
    cors_origins = os.environ.get("SKINNYWMS_CORS_ORIGINS", "")
    if cors_origins == "":
        return None
    if cors_origins == "*":
        return "*"
    return cors_origins.split(",")


def _env_static_path():
    static_path = os.environ.get("SKINNYWMS_STATIC_PATH", "")
    if static_path != "":
        return os.path.abspath(os.path.expanduser(static_path))
    if os.path.isdir(package_static):
        return os.path.abspath(package_static)
    return ""


def _build_parser():
    parser = argparse.ArgumentParser(description="Simple WMS server")

    parser.add_argument(
        "-f",
        "--path",
        default=_env_data_path(),
        help="Path to a GRIB or NetCDF file, or a directory\
                         containing GRIB and/or NetCDF files.",
    )
    parser.add_argument(
        "--style", default="", help="Path to a directory where to find the styles"
    )

    parser.add_argument(
        "--user_style",
        default="",
        help="Path to a json file containing the style to use",
    )

    parser.add_argument("--host", default="127.0.0.1", help="Hostname")
    parser.add_argument("--port", default=5000, help="Port number")
    parser.add_argument(
        "--baselayer",
        default="",
        help="Path to a directory where to find the baselayer",
    )
    parser.add_argument(
        "--magics-prefix",
        default="magics",
        help="prefix used to pass information to magics",
    )

    parser.add_argument(
        "--enable-dimension-grouping",
        action="store_true",
        help="Group together layers by more than the time dimension, e.g. by elevation",
    )

    parser.add_argument(
        "--dark-mode",
        action="store_true",
        default=False,
        help="Enable dark mode for default layers and legend graphics",
    )

    parser.add_argument(
        "--omit-default-layers",
        action="store_true",
        default=False,
        help="Omit default layers from the WMS response",
    )

    parser.add_argument(
        "--cors-origins",
        default="",
        help="Comma-separated list of CORS origins, e.g. http://localhost:5000, https://example.com or '*' to allow all origins. If not specified, CORS is disabled.",
    )

    parser.add_argument(
        "--static-path",
        default=_env_static_path(),
        help="Path to static assets directory served at /static. Defaults to SKINNYWMS_STATIC_PATH or packaged assets when available.",
    )

    parser.add_argument(
        "--version",
        action="version",
        version=f"skinnywms {__version__}",
    )

    return parser


def _parse_args(argv=None):
    return _build_parser().parse_args(argv)


def _apply_args(args):
    dark_mode_enabled = _env_bool("SKINNYWMS_DARK_MODE")
    omit_default_layers = _env_bool("SKINNYWMS_OMIT_DEFAULT_LAYERS")
    enable_dimension_grouping = _env_bool("SKINNYWMS_ENABLE_DIMENSION_GROUPING")
    origins = _env_origins()

    if args.style != "":
        os.environ["MAGICS_STYLE_PATH"] = args.style + ":ecmwf"

    if args.user_style != "":
        os.environ["MAGICS_USER_STYLE_PATH"] = args.user_style

    if args.dark_mode:
        dark_mode_enabled = True

    if args.omit_default_layers:
        omit_default_layers = True

    if args.cors_origins:
        origins = "*" if args.cors_origins == "*" else args.cors_origins.split(",")

    static_path = args.static_path
    if static_path != "":
        static_path = os.path.abspath(os.path.expanduser(static_path))
        if not os.path.isdir(static_path):
            LOG.warning("Static path does not exist or is not a directory: %s", static_path)
            static_path = ""
    application.config["SKINNYWMS_STATIC_PATH"] = static_path

    if origins:
        # Enable CORS for all endpoints
        CORS(application, resources={r"/*": {"origins": origins}})
        LOG.info("CORS enabled for all endpoints. Allowed origins: %s", origins)

    group_dimensions = args.enable_dimension_grouping or enable_dimension_grouping

    server = WMSServer(
        Availability(args.path, group_dimensions=group_dimensions),
        Plotter(
            args.baselayer,
            dark_mode=dark_mode_enabled,
            omit_default_layers=omit_default_layers,
        ),
        Styler(args.user_style, dark_mode=dark_mode_enabled),
    )

    server.magics_prefix = args.magics_prefix
    return server


server = _apply_args(_parse_args([]))


@application.route("/static/<path:filename>", endpoint="static")
def static_files(filename):
    static_path = application.config.get("SKINNYWMS_STATIC_PATH", "")
    if static_path == "":
        abort(404)
    return send_from_directory(static_path, filename)


@application.route("/wms", methods=["GET"])
def wms():
    return server.process(
        request,
        Response=Response,
        send_file=send_file,
        render_template=render_template,
        reraise=True,
    )


@application.route("/availability", methods=["GET"])
def availability():
    return jsonify(server.availability.as_dict())


@application.route("/", methods=["GET"])
def index():
    return render_template("leaflet_demo.html")


def execute():
    global server
    args = _parse_args()
    server = _apply_args(args)
    application.run(port=args.port, host=args.host, debug=True, threaded=False)
