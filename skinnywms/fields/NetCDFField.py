# (C) Copyright 2012-2019 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation nor
# does it submit to any jurisdiction.

import datetime
import logging
import os
from contextlib import closing
from itertools import product

import xarray as xr
from dateutil import parser

from skinnywms import datatypes
from skinnywms.server import WMSServer


def as_datetime(self, time):
    # See https://github.com/numpy/numpy/issues/8546
    # Otherwise we should use 'astype(datetime.datetime)'
    # https://stackoverflow.com/questions/29753060/how-to-convert-numpy-datetime64-into-datetime

    # Lose the nano-seconds.... always assume times in UTC
    try:
        return datetime.datetime.strptime(str(time)[:19], "%Y-%m-%dT%H:%M:%S").replace(
            tzinfo=datetime.timezone.utc
        )
    except:
        return parser.parse(str(time)[:19]).replace(tzinfo=datetime.timezone.utc)


def as_level(self, level):
    n = float(level)
    if int(n) == n:
        return int(n)
    return n


class Slice:
    def __init__(self, name, value, index, is_dimension, is_info):
        self.name = name
        self.index = index
        self.value = value
        self.is_dimension = (not is_info,)
        self.is_info = is_info

    def __repr__(self):
        return "[%s:%s=%s]" % (self.name, self.index, self.value)

    def as_dict(self):
        return dict(
            _class=self.__class__.__module__ + "." + self.__class__.__name__,
            name=self.name,
            index=self.index,
            value=self.value,
            is_dimension=self.is_dimension,
        )


class TimeSlice(Slice):
    pass


class PressureLevelSlice(Slice):
    pass


class ModelLevelSlice(Slice):
    pass


class Coordinate:
    def __init__(self, variable, info):
        self.variable = variable
        # We only support 1D coordinate for now
        # assert len(variable.dims) == 1
        self.is_info = info
        self.is_dimension = not info

        if variable.values.ndim == 0:
            self.values = [self.convert(variable.values)]
        else:
            self.values = [self.convert(t) for t in variable.values]

    def make_slice(self, value):
        return self.slice_class(
            self.variable.name,
            value,
            self.values.index(value),
            self.is_dimension,
            self.is_info,
        )

    def __repr__(self):
        return "%s[name=%s,values=%s]" % (
            self.__class__.__name__,
            self.variable.name,
            len(self.values),
        )


class TimeCoordinate(Coordinate):
    slice_class = TimeSlice
    is_dimension = True
    convert = as_datetime


class ModelLevelCoordinate(Coordinate):
    # This class is just in case we want to specialise
    # 'level', othewise, it is the same as OtherCoordinate
    slice_class = ModelLevelSlice
    is_dimension = True
    convert = as_level


class PressureLevelCoordinate(Coordinate):
    # This class is just in case we want to specialise
    # 'level', othewise, it is the same as OtherCoordinate
    slice_class = PressureLevelSlice
    is_dimension = True
    convert = as_level


class OtherCoordinate(Coordinate):
    slice_class = Slice
    is_dimension = False
    convert = as_level


class NetCDFField(datatypes.Field):

    log = logging.getLogger(__name__)

    def __init__(self, context, path, ds, variable, slices):

        self.path = path
        self.variable = variable
        self.slices = slices

        self.shortName = self.variable
        self.companion = None  # not yet supported for netCDF

        self.longName = getattr(
            ds[self.variable],
            "long_name",
            getattr(ds[self.variable], "standard_name", self.variable),
        )

        self.levelist = None
        # if level:
        #     self.name += '_' + str(level)

        magics_prefix = "magics"

        if hasattr(context, magics_prefix):
            magics_prefix = context.magics_prefix

        self.legend_title = getattr(
            ds[self.variable], "{}_legend_title_text".format(magics_prefix), self.title
        )

        # if level:
        #     self.title += ' @ ' + str(level)

        self.time = None

        for s in self.slices:

            if isinstance(s, TimeSlice):
                self.time = s.value
            elif isinstance(s, PressureLevelSlice):
                # it's a pressure level
                self.levelist = s.value
                self.levtype = "pl"
            elif isinstance(s, ModelLevelSlice):
                # it's a model level
                self.levelist = s.value
                self.levtype = "ml"

        key = "style.netcdf.%s" % (self.name,)

        # Optimisation
        self.styles = context.stash.get(key)
        if self.styles is None:
            self.styles = context.stash[key] = context.styler.netcdf_styles(
                self, ds[variable], path, variable
            )

    @property
    def name(self) -> str:
        # override getter for name
        nameSuffix = (
            "" if self.levelist is None else "@%s_%s" % (self.levtype, self.levelist)
        )

        if self.companion is None:
            return "%s%s" % (self.shortName, nameSuffix)
        else:
            return "%s/%s%s" % (
                self.ucomponent.shortName,
                self.vcomponent.shortName,
                nameSuffix,
            )

    @property
    def group_name(self) -> str:
        # override getter for name
        nameSuffix = "" if self.levelist is None else "@%s" % (self.levtype)

        if self.companion is None:
            return "%s%s" % (self.shortName, nameSuffix)
        else:
            return "%s/%s%s" % (
                self.ucomponent.shortName,
                self.vcomponent.shortName,
                nameSuffix,
            )

    @property
    def title(self) -> str:
        # override getter for title
        titleSuffix = (
            "" if self.levelist is None else " @ %s_%s" % (self.levtype, self.levelist)
        )

        if self.companion is None:
            return "%s%s" % (self.longName, titleSuffix)
        else:
            return "%s/%s%s" % (
                self.ucomponent.longName,
                self.vcomponent.longName,
                titleSuffix,
            )

    @property
    def group_title(self) -> str:
        # override getter for title
        titleSuffix = "" if self.levelist is None else " @ %s" % (self.levtype)

        if self.companion is None:
            return "%s%s" % (self.longName, titleSuffix)
        else:
            return "%s/%s%s" % (
                self.ucomponent.longName,
                self.vcomponent.longName,
                titleSuffix,
            )

    def render(self, context, driver, style, legend={}):

        dimensions = ["%s:%s" % (s.name, s.index) for s in self.slices]
        data = []

        if dimensions:
            params = dict(
                netcdf_filename=self.path,
                netcdf_value_variable=self.variable,
                netcdf_dimension_setting=dimensions,
                netcdf_dimension_setting_method="index",
            )
        else:
            params = dict(
                netcdf_filename=self.path, netcdf_value_variable=self.variable
            )

        # params['netcdf_field_automatic_scaling'] = 'off'

        if style:
            style.adjust_netcdf_plotting(params)

        data.append(driver.mnetcdf(**params))
        data.append(context.styler.contours(self, driver, style, legend))

        return data

    def __repr__(self):
        return "NetCDFField[%r,%r]" % (self.variable, self.slices)

    def as_dict(self):
        return dict(
            _class=self.__class__.__module__ + "." + self.__class__.__name__,
            name=self.name,
            title=self.title,
            path=self.path,
            variable=self.variable,
            slices=[s.as_dict() for s in self.slices],
            styles=[s.as_dict() for s in self.styles],
            time=self.time.isoformat() if self.time is not None else None,
        )


class NetCDFReader(datatypes.FieldReader):
    """Get WMS layers from a NetCDF file."""

    log = logging.getLogger(__name__)

    def __init__(self, context: WMSServer, path: str):
        super(NetCDFReader, self).__init__(context=context, path=path)
        self.log.info("__init__")

    def get_fields(self):
        with closing(xr.open_mfdataset(self.path)) as ds:
            return self._get_fields(ds)

    def _get_fields(self, ds):
        # Select only geographical variables

        self.log.info(
            "Scanning file ===> : %s (size=%s)", self.path, os.path.getsize(self.path)
        )

        fields = []

        skip = set()

        for name in ds.data_vars:

            v = ds[name]
            skip.update([c for c in getattr(v, "coordinates", "").split(" ")])
            skip.update([c for c in getattr(v, "bounds", "").split(" ")])

        for name in ds.data_vars:

            if name in skip:
                continue

            v = ds[name]

            coordinates = []

            # self.log.info('Scanning file: %s var=%s coords=%s', self.path, name, v.coords)

            info = [value for value in v.coords if value not in v.dims]

            has_lon = False
            has_lat = False

            for coord in v.coords:
                c = ds[coord]

                # self.log.info("COORD %s %s %s %s", coord, type(coord), hasattr(c, 'calendar'), c)

                standard_name = getattr(c, "standard_name", None)
                axis = getattr(c, "axis", None)
                long_name = getattr(c, "long_name", None)

                use = False

                if standard_name in ("longitude", "projection_x_coordinate") or (
                    long_name == "longitude"
                ):
                    has_lon = True
                    use = True

                if standard_name in ("latitude", "projection_y_coordinate") or (
                    long_name == "latitude"
                ):
                    has_lat = True
                    use = True

                # TODO: Support other level types

                # Of course, not every one sets the standard_name
                if standard_name in ("time", "forecast_reference_time") or axis == "T":
                    coordinates.append(TimeCoordinate(c, coord in info))
                    use = True
                elif standard_name in (
                    "air_pressure",
                    "altitude",
                    "plev",  # era5 pressure levels
                    "isobaricInhPa",
                ):  # or axis == 'Z':
                    # see also https://cfconventions.org/Data/cf-standard-names/current/build/cf-standard-name-table.html
                    coordinates.append(PressureLevelCoordinate(c, coord in info))
                    use = True
                elif standard_name in ("model_level_number",):  # or axis == 'Z':
                    coordinates.append(ModelLevelCoordinate(c, coord in info))
                    use = True

                if not use:
                    coordinates.append(OtherCoordinate(c, coord in info))

            if not (has_lat and has_lon):
                self.log.info("NetCDFReader: skip %s (Not a 2 field)", name)
                continue

            for values in product(*[c.values for c in coordinates]):

                slices = []
                for value, coordinate in zip(values, coordinates):
                    self.log.info("COORDINATE %s:%s" % (coordinate, value))
                    slices.append(coordinate.make_slice(value))

                fields.append(NetCDFField(self.context, self.path, ds, name, slices))

        if not fields:
            raise Exception("NetCDFReader no 2D fields found in %s", self.path)

        self.log.info("Scanning file <=== : %s (fields=%s)", self.path, len(fields))

        return fields
