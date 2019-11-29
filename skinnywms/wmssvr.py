# (C) Copyright 2012-2019 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation nor
# does it submit to any jurisdiction.

import os
import argparse

from flask import Flask, request, Response, render_template, send_file, jsonify

from .server import WMSServer
from .plot.magics import Plotter, Styler


application = Flask(__name__)

demo = os.path.join(os.path.dirname(__file__),
                    'testdata',
                    'sfc.grib')

demo = os.environ.get("SKINNYWMS_DATA_PATH", demo)

parser = argparse.ArgumentParser(description='Simple WMS server')

parser.add_argument('-f', '--path',
                    default=demo,
                    help='Path to a GRIB or NetCDF file, or a directory\
                         containing GRIB and/or NetCDF files.')
parser.add_argument('--style',
                    default='',
                    help='Path to a directory where to find the styles')
parser.add_argument('--host',
                    default="127.0.0.1",
                    help='Hostname')
parser.add_argument('--port',
                    default=5000,
                    help='Port number')
parser.add_argument('--baselayer',
                    default='',
                    help='Path to a directory where to find the baselayer')


args = parser.parse_args()

if args.style != '':
    os.environ["MAGICS_STYLE_PATH"] = args.style + ":ecmwf"


mv_layers_conf = os.getenv('ECMWF_MV_LAYERS_CONFIG', '')

if mv_layers_conf == '':
    from .data.fs import Availability
    server = WMSServer(
        Availability(args.path),
        Plotter(args.baselayer),
        Styler())
else:
    from .data.mvfs import MvAvailability
    server = WMSServer(
        MvAvailability(mv_layers_conf),
        Plotter(),
        Styler())
    server.args = args

@application.route('/wms', methods=['GET'])
def wms():
    return server.process(request,
                          Response=Response,
                          send_file=send_file,
                          render_template=render_template,
                          reraise=True)


@application.route('/availability', methods=['GET'])
def availability():
    return jsonify(server.availability.as_dict())


@application.route('/', methods=['GET'])
def index():
    return render_template('leaflet_demo.html')


def execute():

    application.run(port=args.port, host=args.host, debug=True, threaded=False)

