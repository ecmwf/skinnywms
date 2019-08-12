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
from .data.fs import Availability
from .plot.magics import Plotter, Styler


application = Flask(__name__)

demo = os.path.join(os.path.dirname(__file__),
                    '..',
                    'testdata',
                    'sfc.grib')

parser = argparse.ArgumentParser(description='Simple WMS server')

parser.add_argument('--path',
                    default=demo,
                    help='Path to a GRIB or NetCDF file, or a directory containing GRIB and/or NetCDF files.')
parser.add_argument('--style',
                    default='',
                    help='Path to a directory where to find the styles')


args = parser.parse_args()

if args.style != '':
    os.environ["MAGICS_STYLE_PATH"] = args.style+ ":ecmwf"
server = WMSServer(
    Availability(args.path),
    Plotter(),
    Styler())


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

