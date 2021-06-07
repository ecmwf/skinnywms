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


wind_companions = { "10u" : "10v", "u" : "v", "U_10m" : "V_10m", "U" : "V" }
"""A collection of wind u-component/v-component (key/value) grib shortName pairs that may be paired for better visualisation as wind barbs."""
wind_ucomponents = set(wind_companions.keys())
"""A collection grib shortNames that represend wind u-components"""
wind_vcomponents = set(wind_companions.values())

# add the inverse combination as well to make matching independent of the order in which fields are processed
for key,value in list(wind_companions.items()):
    wind_companions[value] = key

possible_matches = {}
"""a collection of imported fields that could have companions
which is filled during init process"""

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
        self.companion = None

        if grib.levtype == "sfc":
            self.name = grib.shortName
            self.title = grib.name
        else:
            self.name = "%s_%s" % (grib.shortName, grib.levelist)
            self.title = "%s at %s" % (grib.name, grib.levelist)
            self.levelist = grib.levelist

        # check if this field could have a companion field (e.g. wind components)
        if self.shortName in wind_companions:
            companion_name = wind_companions[self.shortName]
            # get the possible companions that have already been found
            # but haven't been matched up with other fields
            possible_companions = possible_matches.get(companion_name, []) 
            
            for possible_companion in possible_companions:
                # check if this companion matches
                found = self.matches(possible_companion)
                if found:
                    self.companion = possible_companion
                    break

            if self.companion is None:
                # if we didn't manage to match up this field with another one
                # we'll keep it for later
                if self.name not in possible_matches: 
                    possible_matches[self.name] = [self]
                else:
                    # there could be multiple fields with same name (shortName)
                    # but different time or level properties
                    # for matching, so remember them all
                    # as possible candidates for matching
                    possible_matches[self.name].append(self)
    
        key = "style.grib.%s" % (self.name,)

        # Optimisation
        self.styles = context.stash.get(key)
        if self.styles is None:
            self.styles = context.stash[key] = context.styler.grib_styles(
                self, grib, path, index
            )

    def matches(self, companion):
        """Check if companion has matching grib properties time, levtype and levelist.

        :param companion: a grib field that can be used in combination to visualise self
        :type companion: GRIBField
        :return: True if companion matches the properties of self, else False
        :rtype: bool
        """
        if self.time != companion.time: 
            return False
        if self.levtype != companion.levtype: 
            return False
        if self.levtype != "sfc":
            if self.levelist != companion.levelist: 
                return False
        #  Found a match WE have a vector
        self.render = self.render_wind
        if self.name in wind_ucomponents:
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

    def __eq__(self, other):
        if isinstance(other, GRIBField):
            return self.__hash__() == other.__hash__()
        else:
            return False

    def __hash__(self):
        return hash(self.__repr__())


class GRIBReader:

    """Get WMS layers from a GRIB file."""

    log = logging.getLogger(__name__)

    def __init__(self, context, path):
        self.path = path
        self.context = context

    def get_fields(self):
        self.log.info("Scanning file: %s", self.path)

        fields = set()

        for i, m in enumerate(grib_bindings.GribFile(self.path)):
            fields.add(GRIBField(self.context, self.path, m, i))
        
        # remove fields that were successfully matched 
        # and will be diplayed together with their companion
        companionfields = {item.companion for item in fields if not item.companion is None}
        for gribfield in companionfields:
            if gribfield in fields:
                fields.remove(gribfield)

        if not fields:
            raise Exception("GRIBReader no 2D fields found in %s", self.path)

        return list(fields)
