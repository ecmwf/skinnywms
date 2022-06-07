# (C) Copyright 2012-2019 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation nor
# does it submit to any jurisdiction.

from threading import settrace
from typing import Dict
import weakref
from skinnywms.grib_bindings.GribField import GribField
from skinnywms.server import WMSServer
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

    def __init__(self, context: WMSServer, path: str, grib:GribField, index:int):
        super(datatypes.Field,self).__init__()

        self.path = path
        self.index = index
        self.mars = grib.mars_request
        self.render = self.render_contour
        self.byte_offset = grib.byte_offset

        self.metadata = grib.metadata

        self.context = context

        self.time = grib.valid_date

        self.levtype = grib.levtype
        if self.levtype == "150": self.levtype = "ml" # DWD ICON hack

        self.shortName = grib.shortName
        self.longName = grib.name
        self.levelist = grib.levelist if hasattr(grib,"levelist") and grib.levtype != "sfc" else None # None = 2d field

        self.companion = None

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
                    self.update_companions(companion=possible_companion)
                    break

            if self.companion is None:
                # if we didn't manage to match up this field with another one
                # we'll keep it for later
                if self.shortName not in possible_matches: 
                    possible_matches[self.shortName] = [self]
                else:
                    # there could be multiple fields with same name (shortName)
                    # but with different time or level properties
                    # for matching, so remember them all
                    # as possible candidates for matching
                    possible_matches[self.shortName].append(self)

        key = "style.grib.%s" % (self.name,)
        
        # Optimisation
        self.styles = context.stash.get(key)
        if self.styles is None:
            self.styles = context.stash[key] = context.styler.grib_styles_from_meta(self)

    @property
    def metadata(self) -> Dict[str,str]:
        if self.companion is None:
            return self._metadata
        else:
            joined_meta = {}
            common_keys = set(self.ucomponent._metadata.keys()).intersection(set(self.vcomponent._metadata.keys()))
            for key in common_keys:
                joined_meta[key] = "%s/%s" % (self.ucomponent._metadata[key], self.vcomponent._metadata[key])
            return joined_meta
    
    @metadata.setter
    def metadata(self, metadata:Dict[str,str]):
        self._metadata = metadata

    
    @property
    def context(self) -> WMSServer:
        return self._context()
    
    @property
    def magics_metadata():
        return {
            ""
        }

    @context.setter
    def context(self, context:WMSServer):
        self._context = weakref.ref(context)

    def matches(self, other) -> bool:
        """Check if companion has matching grib properties (filename, time, levtype and levelist).

        :param companion: a grib field that can be used in combination to visualise self
        :type companion: GRIBField
        :return: True if companion matches the properties of self, else False
        :rtype: bool
        """
        if self.path != other.path:
            # TODO: matching up wind components from two different grib files is not supported in magics yet
            return False
        if self.time != other.time:
            return False
        if self.levtype != other.levtype:
            return False
        if self.levelist != other.levelist: 
            return False
        return True

    def update_companions(self, companion):
        """Updates/overwrites self.companion with the given companion and vice versa. 
        Updates render function and ucomponent and vcomponent attributes for 
        self and companion.

        :param companion: the new companion field
        :type companion: GRIBField
        """
        # found a match (right now it's always wind components)
        self.companion = companion
        companion.companion = self

        # remember wind components u,v
        self.ucomponent = self if self.shortName in wind_ucomponents else companion
        self.vcomponent = companion if self.shortName in wind_ucomponents else self

        companion.ucomponent = self.ucomponent
        companion.vcomponent = self.vcomponent

        # render these fields as wind
        self.render = self.render_wind
        companion.render = companion.render_wind

        key = "style.grib.%s" % (self.name,)
        self.styles = self.context.stash[key] = self.context.styler.grib_styles_from_meta(self)
        companion.styles = self.styles

    @property
    def name(self) -> str:
        # override getter for name
        nameSuffix = "" if self.levelist is None else "@%s_%s" % (self.levtype, self.levelist)

        if self.companion is None:
            return "%s%s" % (self.shortName, nameSuffix)
        else:
            return "%s/%s%s" % (self.ucomponent.shortName, self.vcomponent.shortName, nameSuffix)

    @property
    def group_name(self) -> str:
        # override getter for name
        nameSuffix = "" if self.levelist is None else "@%s" % (self.levtype)

        if self.companion is None:
            return "%s%s" % (self.shortName, nameSuffix)
        else:
            return "%s/%s%s" % (self.ucomponent.shortName, self.vcomponent.shortName, nameSuffix)

    @property
    def title(self) -> str:
        # override getter for title
        titleSuffix = "" if self.levelist is None else " @ %s_%s" % (self.levtype, self.levelist)

        if self.companion is None:
            return "%s%s" % (self.longName, titleSuffix)
        else:
            return "%s/%s%s" % (self.ucomponent.longName, self.vcomponent.longName,titleSuffix)

    @property
    def group_title(self) -> str:
        # override getter for title
        titleSuffix = "" if self.levelist is None else " @ %s" % (self.levtype)

        if self.companion is None:
            return "%s%s" % (self.longName, titleSuffix)
        else:
            return "%s/%s%s" % (self.ucomponent.longName, self.vcomponent.longName,titleSuffix)

    def render_contour(self, context, driver, style, legend={}) -> list:
        data = []
        params = dict(
            grib_input_file_name=self.path, 
            grib_field_position=self.byte_offset, 
            grib_file_address_mode="byte_offset"
        )

        if style:
            style.adjust_grib_plotting(params)

        data.append(driver.mgrib(**params))
        data.append(context.styler.contours(self, driver, style, legend))

        return data
    
    def render_wind(self, context, driver, style, legend={}) -> list:
        data = []

        params = dict(
            grib_input_file_name = self.path, 
            grib_wind_position_1 = self.ucomponent.byte_offset, 
            grib_wind_position_2 = self.vcomponent.byte_offset,
            grib_file_address_mode="byte_offset"
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

    def __repr__(self) -> str:
        return "GRIBField[%r,%r,%r]" % (self.path, self.index, self.mars)

    def __eq__(self, other) -> bool:
        if isinstance(other, GRIBField):
            return self.__hash__() == other.__hash__()
        else:
            return False

    def __hash__(self) -> int:
        return hash(self.__repr__())


class GRIBReader(datatypes.FieldReader):

    """Get WMS layers from a GRIB file."""

    log = logging.getLogger(__name__)

    def __init__(self, context:WMSServer, path:str):
        super(GRIBReader,self).__init__(context=context, path=path)

    def get_fields(self) -> list:
        self.log.info("Scanning file: %s", self.path)

        fields = set()

        for i, m in enumerate(grib_bindings.GribFile(self.path)):
            fields.add(GRIBField(self.context, self.path, m, i))

        if not fields:
            raise Exception("GRIBReader no 2D fields found in %s", self.path)

        # fields that were successfully matched with their companion fields
        # carry the same layer name and thus will be removed at a later stage
        return list(fields)
