# (C) Copyright 2012-2019 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation nor
# does it submit to any jurisdiction.

from skinnywms import datatypes
import logging
import os
import datetime



class GeoJSONField(datatypes.Field):

    log = logging.getLogger(__name__)

    def __init__(self, context, path):

        self.path = path
        
        self.time = datetime.datetime.now()
        name = os.path.basename(path)
        self.name, ext = os.path.splitext(name)
        self.title = self.name

        self.styles=["symbol"]

    

    def render(self, context, driver, style, legend={}):
        data = []

        data.append(driver.mgeojson(geojson_input_filename = self.path))
        data.append(context.styler.symbol(self, driver, style, legend))

        return data

    def as_dict(self):
        return dict(
            _class=self.__class__.__module__ + "." + self.__class__.__name__,
            name=self.name,
            title=self.title,
            path=self.path,
            index=self.index,
            mars=self.mars,
            styles=[s.as_dict() for s in self.styles],
            time=self.time.isoformat() if self.time is not None else None,
        )

    def __repr__(self):
        return "GRIBField[%r,%r,%r]" % (self.path, self.index, self.mars)


class GeoJSONReader:

    """Get WMS layers from a GRIB file."""

    log = logging.getLogger(__name__)

    def __init__(self, context, path):
        self.path = path
        self.context = context

    def get_fields(self):
        self.log.info("Scanning file: %s", self.path)
        print("Scanning file: %s", self.path)

        fields = [ GeoJSONField(self.context, self.path) ]

        

        return fields
