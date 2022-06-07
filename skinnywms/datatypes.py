# -*- coding: future_annotations -*-
# from __future__ import annotations
from abc import ABC, abstractmethod # see https://www.python.org/dev/peps/pep-0563/
# (C) Copyright 2012-2019 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation nor
# does it submit to any jurisdiction.

import datetime
import logging
from skinnywms.server import WMSServer
from skinnywms import errors

from typing import List, Dict

import weakref

__all__ = [
    "Availability",
    "CRS",
    "Layer",
    "Plotter",
    "Style",
]

LOG = logging.getLogger(__name__)


class CRS:
    def __init__(self, name, n_lat, s_lat, w_lon, e_lon):
        self.name = name
        self.n_lat = n_lat
        self.s_lat = s_lat
        self.w_lon = w_lon
        self.e_lon = e_lon


class StyleConfig:
    def __init__(self, verb, config):
        self.verb = verb
        self.config = config

    def as_dict(self):
        return dict(
            _class=self.__class__.__module__ + "." + self.__class__.__name__,
            verb=self.verb,
            config=self.config,
        )


class Style:
    def __init__(self, name, title=None, description=None, legend=None, config=None):
        self.name = name
        self.title = title is not None and title or name
        self.description = description is not None and description or name
        self.config = config

    def as_dict(self):
        return dict(
            _class=self.__class__.__module__ + "." + self.__class__.__name__,
            name=self.name,
            title=self.title,
            description=self.description,
            config=[s.as_dict() for s in self.config],
        )

    def adjust_netcdf_plotting(self, params):
        pass

    def adjust_grib_plotting(self, params):
        pass


class Field:
    def style(self, name:str) -> str:

        if name == "":
            if self.styles:
                return self.styles[0]
            else:
                return None

        for s in self.styles:
            if s.name == name:
                return s

        raise errors.StyleNotDefined(name)

    @property
    def name(self) -> str:
        if self._name:
            return self._name
        else:
            return "undefined"

    @name.setter
    def name(self, value:str) -> None:
        self._name = value

    @property
    def group_name(self) -> str:
        if self._group_name:
            return self._group_name
        else:
            return self.name  # fallback to name if unset

    @group_name.setter
    def group_name(self, value:str) -> None:
        self._group_name = value

    @property
    def title(self) -> str:
        if self._title:
            return self._title
        else:
            return "undefined"

    @title.setter
    def title(self, value:str) -> None:
        self._title = value

    @property
    def group_title(self) -> str:
        if self._group_title:
            return self._group_title
        else:
            return self.title  # fallback to title if unset

    @group_title.setter
    def group_title(self, value:str) -> None:
        self._group_title = value

    @property
    def companion(self) -> Field:
        if self._companion:
            return self._companion
        else:
            return None

    @companion.setter
    def companion(self, value:Field) -> Field:
        self._companion = value


class FieldReader(ABC):
    """Get WMS layers (fields) from a file."""

    def __init__(self, context:WMSServer, path:str) -> None:
        self._context = context
        self._path = path

    @property
    def context(self) -> WMSServer:
        return self._context
    
    @context.setter
    def context(self, context:WMSServer) -> None:
        self._context = weakref.ref(context)
    
    @property
    def path(self) -> str:
        return self._path
    
    @path.setter
    def path(self, path:str) -> None:
        self._path = path
    
    @abstractmethod
    def get_fields(self) -> List[Field]:
        """Returns a list of wms layers (fields)

        :raises NotImplementedError: [description]
        :return: a list of wms layers (fields)
        :rtype: List[Field]
        """
        raise NotImplementedError()

class Layer:
    def __init__(self, name:str, title:str, zindex:int=0, description:str=None, keywords:List[str]=[]):
        self.name = name
        self.title = title
        self.legend_title = self.title
        self.description = description
        self.zindex = zindex
    
    def add_field(self, field: Field) -> None:
        """Adds a data field to this layer to group together data for the same parameter,
        e.g. with different time or elevation dimension.

        :param field: the field to add to this layer
        :type field: Field
        """
        raise NotImplementedError()


class Dimension:
    def __init__(self, name:str, units:str, default:str, extent:str, unitSymbol:str):
        self.name = name
        self.units = units
        self.default = default
        self.extent = extent
        self.unitSymbol = unitSymbol
    
    def add_field(self, field:Field) -> None:
        """Adds a data field to this dimension to group together data for the same parameter,
        that has the same dimensionality (e.g. time and elevation), but a different extent.

        Example(s):
        - pressure at mean sea level at 09:00 UTC and at 10:00 UTC
        - temperature at 12:00 UTC at 2m and temperature at 12:00 UTC at 10m
        - soil temperature at 5mm and soil temperature at 10mm

        :param field: the field to add to this dimension
        :type field: Field
        """
        raise NotImplementedError()


class TimeDimension(Dimension):
    def __init__(self, times:List[datetime.datetime]):
        super(TimeDimension, self).__init__(
            name = "time", 
            units = "ISO8601",
            default = None,
            extent = "",
            unitSymbol=None)
        times = sorted(times)
        self.default = times[0].isoformat() + "Z"

        self.extent = TimeDimension.format_extent(times)
    
    def format_extent(times:List[datetime.datetime]) -> str:
        """Formats a sorted list of times as WMS time extent string.

        :param times: a sorted list of times
        :type times: List[datetime.datetime]
        :return: the WMS time extent string
        :rtype: str
        """
        extent = []
        last_delta = None
        last_iso_ts = None
        prev_time = times[0]

        # build the textual representation of the time dimension extent
        for time in times:
            iso_ts = time.isoformat() + "Z"

            delta = time - prev_time
            prev_time = time
            if delta == last_delta and delta != datetime.timedelta(0):
                extent[-1] = "/".join([last_iso_ts, iso_ts, TimeDimension.format_iso_8601_duration(delta)])
            else:
                extent.append(iso_ts)
                last_delta = delta
                last_iso_ts = iso_ts

        return ",".join(extent)
    
    def format_iso_8601_duration(period:datetime.timedelta) -> str:
        """Converts a timedelta object into ISO 8601 duration/period format.

        :param period: the period to be converted
        :return: the period in ISO 8601 duration format
        :rtype: str
        """

        ret = "P"
        if period.days != 0:
            ret += "%dD" % period.days

        if period.seconds > 0 or period.microseconds > 0:
            ret += "T"
        else:
            return ret # no seconds or microseconds in this period

        remainder_s = period.seconds
        if remainder_s >= 3600:
            ret += "%dH" % (remainder_s / 3600) # extract whole hours
            remainder_s = remainder_s % 3600

        if remainder_s >= 60:
            ret += "%dM" % (remainder_s / 60) # extract whole minutes
            remainder_s = remainder_s % 60

        if remainder_s > 0 and period.microseconds == 0:
            ret += "%dS" % remainder_s # only whole seconds
        elif period.microseconds > 0:
            ret += "%fS" % (remainder_s + period.microseconds/1000000) # floating point number
        return ret


class ElevationDimension(Dimension):
    """An elevation dimension representing vertical 'levels' as described in
    https://external.ogc.org/twiki_public/pub/MetOceanDWG/MetOceanWMSBPOnGoingDrafts/12-111r1_Best_Practices_for_WMS_with_Time_or_Elevation_dependent_data.pdf

    Most common cases:

    1) Numeric elevation values, e.g isobaric (pressure) levels in [hPa] or isometric levels in [m]
    <Dimension name="elevation" units="hectoPascal" unitSymbol="hPa" default="1000" multipleValues="0" nearestValue="0" current="0">100,200,500,1000</Dimension>

    2) Named surfaces
    <Dimension name="elevation" units="computed_surface" unitSymbol="" default="0" multipleValues="0" nearestValue="0" current="0">1/90/1</Dimension>
    """
    def __init__(self, levels:List[str], default:str, units:str="computed_surface", unitSymbol:str=""):
        super(ElevationDimension, self).__init__(
            name = "elevation", 
            units = units,
            default = default,
            extent = ",".join(levels),
            unitSymbol = unitSymbol
        )

        if self.default is None and len(levels) > 0:
            self.default = levels[0]
        
        # TODO: process list of levels to fill extent
        # ...
    
    def add_field(self, field: Field) -> None:
        pass

class DataLayer(Layer):

    # TODO: check the time-zone of the dates....

    def __init__(self, field:Field, group_dimensions:bool=False) -> None:
        self._group_dimensions = group_dimensions
        if self._group_dimensions:
            super(DataLayer, self).__init__(field.group_name, field.group_title)
        else:
            super(DataLayer, self).__init__(field.name, field.title)
        assert field.time is None or isinstance(field.time, datetime.datetime)
        assert field.levelist is None or isinstance(field.levelist, int)
        self._first = field

        self._fields = {(field.time, field.levelist): field}

    @property
    def group_dimensions(self) -> bool:
        """If set to 'True', fields are grouped together as layers if they differ in more than
        the time dimension, e.g. in time and elevation dimension.

        :return: 'True' if dimension grouping is enabled, else 'False'
        :rtype: bool
        """
        return self._group_dimensions

    def add_field(self, field: Field) -> None:
        if self._group_dimensions:
            assert self.name == field.group_name

            if self.title != field.group_title:
                raise Exception(
                    "Title redefined for %s [%s] => [%s]" % (self, self.title, field.group_title)
                )

            # Cannot have a mix of None and Dates
            assert field.time is not None or isinstance(field.time, datetime.datetime)
            assert field.levelist is None or isinstance(field.levelist, int)

            if (field.time, field.levelist) in self._fields:
                LOG.info(
                    "Duplicate field (time: %s, elevation: %s) in %s (%s, %s)"
                    % (field.time, field.levelist, self, field, self._fields[(field.time, field.levelist)])
                )

                # # Why are we sometimes throwing this exception .. : need to be checked
                # raise Exception(
                #     "Duplicate date %s in %s (%s, %s)"
                #     % (field.time, self, field, self._fields[field.time])
                # )

            self._fields[(field.time, field.levelist)] = field

        else: # don't group levels
            assert self.name == field.name

            if self.title != field.title:
                raise Exception(
                    "Title redefined for %s [%s] => [%s]" % (self, self.title, field.title)
                )

            # Cannot have a mix of None and Dates
            assert field.time is not None or isinstance(field.time, datetime.datetime)
            assert field.levelist is None or isinstance(field.levelist, int)

            if (field.time, field.levelist) in self._fields:
                LOG.info(
                    "Duplicate field (time: %s, elevation: %s) in %s (%s, %s)"
                    % (field.time, field.levelist, self, field, self._fields[(field.time, field.levelist)])
                )

                # # Why are we sometimes throwing this exception .. : need to be checked
                # raise Exception(
                #     "Duplicate date %s in %s (%s, %s)"
                #     % (field.time, self, field, self._fields[field.time])
                # )

            self._fields[(field.time, field.levelist)] = field

    @property
    def fixed_layer(self):
        return self._first.time is None

    @property
    def dimensions(self):
        dims = []
        if not self.fixed_layer:
            times = sorted(list({l[0] for l in self._fields.keys()}))
            if len(times) > 0:
                dims.append(TimeDimension(times))
            elevation = sorted(list({str(l[1]) for l in self._fields.keys() if l[1] is not None}))
            if len(elevation) > 0:
                elev_units = "computed_surface"
                unit_symbol = ""
                if self._first.levtype == "pl":
                    # pressure levels
                    # TODO: see if you can get the 
                    elev_units = "hectoPascal"
                    unit_symbol = "hPa"

                dims.append(
                    ElevationDimension(
                        # levels = [str(l) for l in range(100,1000,100)],
                        levels = elevation,
                        units=elev_units,
                        default=None,
                        unitSymbol=unit_symbol
                    )
                )
        return dims

    @property
    def styles(self):
        # Assumes all styles shared
        return self._first.styles

    def __repr__(self):
        return "DataLayer[%s]" % (self.name,)

    def select(self, dims):
        # TODO: select on more dimensions
        if dims is None:
            return self._first
        
        time = dims.get("time", None) # try get time string
        elevation = dims.get("elevation", None) # try get elevation string
        LOG.info("Look up layer with %s and time %s (%s) and elevation %s (%s)" % (self, time, type(time), elevation, type(elevation)))

        if time is None:
            time = self._first.time
        else:
            # parse string date
            time = datetime.datetime.strptime(time[:19], "%Y-%m-%dT%H:%M:%S")

        if elevation is None:
            elevation = [i[1] for i in self._fields.keys() if i[0] == time].pop(0)
        else:
            # parse int elevation
            elevation = int(elevation)
 
        if (time,elevation) not in self._fields.keys():
            raise KeyError("(%s,%s) not found. Available combinations: %s" % (time,elevation, self._fields.keys()))

        return self._fields[(time,elevation)]

    def as_dict(self):
        return dict(
            _class=self.__class__.__module__ + "." + self.__class__.__name__,
            fields=[field.as_dict() for _, field in sorted(self._fields.items())],
        )


class Availability:
    def __init__(self, auto_add_plotter_layers:bool=True, group_dimensions:bool=False):
        self._context = None
        self._layers:Dict[str,DataLayer] = {}
        self._aliases = {}
        self._auto_add_plotter_layers = auto_add_plotter_layers
        self._group_dimensions=group_dimensions

    @property
    def context(self) -> WMSServer:
        return self._context()

    # @context.setter
    def set_context(self, context:WMSServer):
        self._context = weakref.ref(context)

    @property
    def group_dimensions(self) -> bool:
        """If set to 'True', fields are grouped together as layers if they differ in more than
        the time dimension, e.g. in time and elevation dimension.

        :return: 'True' if dimension grouping is enabled, else 'False'
        :rtype: bool
        """
        return self._group_dimensions

    @property
    def auto_add_plotter_layers(self) -> bool:
        return self._auto_add_plotter_layers

    def add_field(self, field:Field) -> None:
        """Adds a data field to the list of available layers. 
        
        If a layer with the same name as the field already exists,
        the field is added to the existing layer.

        :param field: the field to be added
        :type field: Field
        """
        # TODO: Use config....

        if self._group_dimensions:
            if not self._layers:
                self._aliases["default"] = field.group_name

            if field.group_name in self._layers:
                # field with the same name already
                # exists, so try to group
                self._layers[field.group_name].add_field(field)
            else:
                self._layers[field.group_name] = DataLayer(field, group_dimensions=self.group_dimensions)
        else: # don't group dimensions
            if not self._layers:
                self._aliases["default"] = field.name

            if field.name in self._layers:
                # field with the same name already
                # exists, so try to group
                self._layers[field.name].add_field(field)
            else:
                self._layers[field.name] = DataLayer(field, group_dimensions=self.group_dimensions)

    def layers(self):
        if not self._layers:
            self.load()
        # return a sorted list
        ret = [l for l in self._layers.values()]
        ret.sort(key=lambda x: x.name, reverse = False)
        return ret

    def layer(self, name, dims):
        if not self._layers:
            self.load()

        LOG.info("Look up layer with name %s and dims %s", name, dims)

        while name in self._aliases:
            name = self._aliases[name]

        if name not in self._layers:
            raise errors.LayerNotDefined("Unknown layer '{}'".format(name))

        # TODO: select on othe dimenstions as well
        return self._layers[name].select(dims)

    def as_dict(self):
        if not self._layers:
            self.load()
        return dict(
            _class=self.__class__.__module__ + "." + self.__class__.__name__,
            aliases=self._aliases,
            layers=[layer.as_dict() for layer in self._layers.values()],
        )


class Plotter:
    @property
    def context(self) -> WMSServer:
        return self._context()

    # @context.setter
    def set_context(self, context:WMSServer):
        self._context = weakref.ref(context)

    def layers(self):
        raise NotImplementedError

    @property
    def supported_crss(self):
        raise NotImplementedError

    @property
    def geographic_bounding_box(self):
        raise NotImplementedError

    def plot(
        self,
        context,
        bbox,
        crs,
        format,
        height,
        layers,
        styles,
        version,
        width,
        output=None,
        bgcolor=None,
        elevation=None,
        exceptions=None,
        time=None,
        transparent=None,
    ):
        raise NotImplementedError


class Styler:
    @property
    def context(self) -> WMSServer:
        return self._context()

    # @context.setter
    def set_context(self, context:WMSServer):
        self._context = weakref.ref(context)
