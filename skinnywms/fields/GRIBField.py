# (C) Copyright 2012-2019 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation nor
# does it submit to any jurisdiction.

from skinnywms import datatypes
import logging
from skinnywms import grib_bindings


companions = { "10u" : "10v" , "10v" : "10u" }

ucomponents = ["10u"]
vcomponents = ["10v"]

possible_matches = {}


class GRIBField(datatypes.Field):

    log = logging.getLogger(__name__)

    def __init__(self, context, path, grib, index):

        self.path = path
        self.index = index
        self.mars = grib.mars_request
        self.render = self.render_contour

        self.time = grib.valid_date
        self.levtype = grib.levtype
        self.shortName = grib.shortName

        if grib.levtype == "sfc":
            self.name = grib.shortName
            self.title = grib.name
        else:
            self.name = "%s_%s" % (grib.shortName, grib.levelist)
            self.title = "%s at %s" % (grib.name, grib.levelist)
            self.levelist = grib.levelist

        if self.shortName in companions:
            companion = companions[self.shortName]
            matches = possible_matches.get(companion, [])
            
            found = False
            for match in matches:
                found = self.match(match)
                if found :
                    break; 
            if not found:
                if self.name not in possible_matches: 
                    possible_matches[self.name] = [self]
                else:
                    possible_matches[self.name].append(self)
    
        key = "style.grib.%s" % (self.name,)

        # Optimisation
        self.styles = context.stash.get(key)
        if self.styles is None:
            self.styles = context.stash[key] = context.styler.grib_styles(
                self, grib, path, index
            )

    def match(self, companion):
        if self.time != companion.time: 
            return False
        if self.levtype != companion.levtype: 
            return False
        if self.levtype != "sfc":
            if self.levelist != companion.levelist: 
                return False
        #  Found a match WE have a vector
        self.render = self.render_wind
        if self.name in ucomponents:
            self.ucomponent = self.index
            self.vcomponent = companion.index
            companion.ucomponent = self.index
            companion.vcomponent = companion.index
            if self.levtype == "sfc":
                self.name = "_".format(self.shortName, companion.shortName)
                self.title = "/".format(self.name, companion.name)
            else:
                self.name = "{}_{}_%s" % (self.shortName, companion.shortName, self.levelist)
                self.title = "{}/{} at %s" % (self.shortName, companion.shortName, self.levelist)
            
        else:
            self.vcomponent = self.index
            self.ucomponent = companion.index
            companion.vcomponent = self.index
            companion.ucomponent = companion.index
            if self.levtype == "sfc":
                self.name = "{}/{}".format(companion.shortName, self.shortName)
                self.title = "{}/{}".format(companion.shortName, self.shortName)
            else:
                self.name = "{}_{}_{}".format(companion.shortName, self.shortName, self.levelist)
                self.title = "{}/{} at {}".format(companion.shortName, self.shortName, self.levelist)
        
        
        return True
        


    def render_contour(self, context, driver, style, legend={}):
        data = []
        params = dict(
            grib_input_file_name=self.path, grib_field_position=self.index + 1
        )

        if style:
            style.adjust_grib_plotting(params)

        data.append(driver.mgrib(**params))
        data.append(context.styler.contours(self, driver, style, legend))

        return data
    
    def render_wind(self, context, driver, style, legend={}):
        data = []
        
        params = dict(
            grib_input_file_name = self.path, 
            grib_wind_position_1 = self.ucomponent+1, 
            grib_wind_position_2 = self.vcomponent+1
        )

        if style:
            style.adjust_grib_plotting(params)

        data.append(driver.mgrib(**params))
        data.append(context.styler.winds(self, driver, style, legend))

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


class GRIBReader:

    """Get WMS layers from a GRIB file."""

    log = logging.getLogger(__name__)

    def __init__(self, context, path):
        self.path = path
        self.context = context

    def get_fields(self):
        self.log.info("Scanning file: %s", self.path)

        fields = []

        for i, m in enumerate(grib_bindings.GribFile(self.path)):
            fields.append(GRIBField(self.context, self.path, m, i))

        if not fields:
            raise Exception("GRIBReader no 2D fields found in %s", self.path)

        return fields
