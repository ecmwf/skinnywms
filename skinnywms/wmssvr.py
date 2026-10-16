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
from urllib.parse import urlsplit

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
from werkzeug.middleware.proxy_fix import ProxyFix

from . import __version__
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


def _env_server():
    server_name = os.environ.get("SKINNYWMS_SERVER", "gunicorn").strip().lower()
    return server_name if server_name in ("gunicorn", "flask") else "gunicorn"


def _env_int(name, default):
    value = os.environ.get(name, "").strip()
    if value == "":
        return default
    try:
        return int(value)
    except ValueError:
        LOG.warning("Invalid integer for %s=%s, using default %s", name, value, default)
        return default


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
        "--server",
        default=_env_server(),
        choices=("gunicorn", "flask"),
        help="WSGI server backend to run (default: gunicorn)",
    )
    parser.add_argument(
        "--gunicorn-workers",
        type=int,
        default=_env_int("SKINNYWMS_GUNICORN_WORKERS", 4),
        help="Number of gunicorn worker processes",
    )
    parser.add_argument(
        "--gunicorn-threads",
        type=int,
        default=_env_int("SKINNYWMS_GUNICORN_THREADS", 8),
        help="Number of threads per gunicorn worker",
    )
    parser.add_argument(
        "--gunicorn-timeout",
        type=int,
        default=_env_int("SKINNYWMS_GUNICORN_TIMEOUT", 120),
        help="Gunicorn worker timeout in seconds",
    )
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
        "--enable-reference-time-dimension",
        action="store_true",
        help="Serve several forecast runs from the same layer, selectable with the\
                         DIM_REFERENCE_TIME parameter. Without this, fields of different\
                         runs sharing a validity time overwrite one another.",
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
        "--trust-x-forwarded",
        action="store_true",
        default=False,
        help=argparse.SUPPRESS,  # deliberately undocumented, see SKINNYWMS_TRUST_XFORWARDED
    )

    parser.add_argument(
        "--public-url",
        default="",
        help="Externally visible base URL of this server (scheme, host and optional path prefix),\
                         e.g. https://example.com/skinny, used for URLs in responses such as\
                         GetCapabilities. Defaults to SKINNYWMS_PUBLIC_URL. If not specified, the URL is\
                         derived from the incoming request.",
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


class _PublicUrlMiddleware:
    """Pins scheme, host and mount prefix of every request to a configured public URL.

    The prefix is expected to be stripped by whatever sits in front of this
    server, i.e. PATH_INFO is left untouched and the prefix goes to SCRIPT_NAME.
    """

    def __init__(self, app, public_url):
        self.app = app
        parts = urlsplit(public_url)
        self.scheme = parts.scheme
        self.host = parts.netloc
        self.prefix = parts.path.rstrip("/")

    def __call__(self, environ, start_response):
        environ["wsgi.url_scheme"] = self.scheme
        environ["HTTP_HOST"] = self.host
        environ["SCRIPT_NAME"] = self.prefix
        return self.app(environ, start_response)


def _validate_public_url(value):
    """Returns the normalized (no trailing slash) public URL, or raises ValueError."""
    parts = urlsplit(value)
    if parts.scheme not in ("http", "https") or not parts.netloc:
        raise ValueError(
            f"Invalid public URL {value!r}: expected http(s)://host[:port][/prefix]"
        )
    if parts.query or parts.fragment:
        raise ValueError(f"Invalid public URL {value!r}: query/fragment not allowed")
    return value.rstrip("/")


def _enable_public_url(public_url):
    """Make Flask treat `public_url` as the externally visible location of this server."""
    public_url = _validate_public_url(public_url)
    wsgi_app = application.wsgi_app
    if isinstance(wsgi_app, _PublicUrlMiddleware):
        wsgi_app = wsgi_app.app  # _apply_args may run more than once
    application.wsgi_app = _PublicUrlMiddleware(wsgi_app, public_url)
    application.config["SKINNYWMS_PUBLIC_URL"] = public_url
    LOG.info("Public URL is %s", public_url)


def _enable_proxy_fix():
    """Make Flask honour X-Forwarded-Proto/-Host/-Prefix from a single trusted proxy."""
    if isinstance(application.wsgi_app, ProxyFix):
        return  # already wrapped, _apply_args may run more than once
    application.wsgi_app = ProxyFix(
        application.wsgi_app, x_for=0, x_proto=1, x_host=1, x_port=0, x_prefix=1
    )
    LOG.info("Trusting X-Forwarded-Proto/-Host/-Prefix headers of a single proxy")


def _public_base_url():
    """Origin plus mount prefix, without trailing slash, as seen by the client."""
    configured = application.config.get("SKINNYWMS_PUBLIC_URL")
    if configured:
        return configured
    return request.host_url.rstrip("/") + request.script_root


def _apply_args(args):
    dark_mode_enabled = _env_bool("SKINNYWMS_DARK_MODE")
    omit_default_layers = _env_bool("SKINNYWMS_OMIT_DEFAULT_LAYERS")
    enable_dimension_grouping = _env_bool("SKINNYWMS_ENABLE_DIMENSION_GROUPING")
    enable_reference_time_dimension = _env_bool(
        "SKINNYWMS_ENABLE_REFERENCE_TIME_DIMENSION"
    )
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
            LOG.warning(
                "Static path does not exist or is not a directory: %s", static_path
            )
            static_path = ""
    application.config["SKINNYWMS_STATIC_PATH"] = static_path

    if origins:
        # Enable CORS for all endpoints
        CORS(application, resources={r"/*": {"origins": origins}})
        LOG.info("CORS enabled for all endpoints. Allowed origins: %s", origins)

    trust_x_forwarded = args.trust_x_forwarded or _env_bool(
        "SKINNYWMS_TRUST_XFORWARDED"
    )
    public_url = args.public_url or os.environ.get("SKINNYWMS_PUBLIC_URL", "").strip()
    if trust_x_forwarded and public_url:
        raise RuntimeError(
            "SKINNYWMS_PUBLIC_URL / --public-url cannot be combined with "
            "SKINNYWMS_TRUST_XFORWARDED / --trust-x-forwarded"
        )
    if public_url:
        _enable_public_url(public_url)
    elif trust_x_forwarded:
        _enable_proxy_fix()

    group_dimensions = args.enable_dimension_grouping or enable_dimension_grouping
    reference_time_dimension = (
        args.enable_reference_time_dimension or enable_reference_time_dimension
    )

    server = WMSServer(
        Availability(
            args.path,
            group_dimensions=group_dimensions,
            reference_time_dimension=reference_time_dimension,
        ),
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
        base_url=_public_base_url(),
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

    if args.server == "flask":
        application.run(port=args.port, host=args.host, debug=True, threaded=False)
        return

    try:
        from gunicorn.app.base import BaseApplication
    except ImportError as exc:
        raise RuntimeError(
            "Gunicorn is not installed. Install skinnywms with gunicorn dependencies or run with '--server flask'."
        ) from exc

    bind = f"{args.host}:{args.port}"
    options = {
        "bind": bind,
        "workers": args.gunicorn_workers,
        "worker_class": "gthread",
        "threads": args.gunicorn_threads,
        "timeout": args.gunicorn_timeout,
    }

    class SkinnyGunicornApplication(BaseApplication):
        def __init__(self, app, gunicorn_options):
            self.application = app
            self.options = gunicorn_options
            super().__init__()

        def load_config(self):
            for key, value in self.options.items():
                if key in self.cfg.settings and value is not None:
                    self.cfg.set(key, value)

        def load(self):
            return self.application

    LOG.info(
        "Starting gunicorn on %s with %s workers x %s threads",
        bind,
        args.gunicorn_workers,
        args.gunicorn_threads,
    )
    SkinnyGunicornApplication(application, options).run()
