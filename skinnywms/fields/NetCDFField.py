# (C) Copyright 2012-2019 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation nor
# does it submit to any jurisdiction.

from skinnywms import datatypes
import logging
import datetime
import os

from contextlib import closing
from itertools import product

import xarray as xr


def as_datetime(self, time):
    # See https://github.com/numpy/numpy/issues/8546
    # Otherwise we should use 'astype(datetime.datetime)'
    # https://stackoverflow.com/questions/29753060/how-to-convert-numpy-datetime64-into-datetime

    # Lose the nano-seconds....
    return datetime.datetime.strptime(str(time)[:19], "%Y-%m-%dT%H:%M:%S")


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
        self.is_dimension = not is_info,
        self.is_info = is_info

    def __repr__(self):
        return "[%s:%s=%s]" % (self.name, self.index, self.value)

    def as_dict(self):
        return dict(_class=self.__class__.__module__ + '.' + self.__class__.__name__,
                    name=self.name,
                    index=self.index,
                    value=self.value,
                    is_dimension=self.is_dimension)


class TimeSlice(Slice):
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
            self.values = [self.convert(t) for t in variable.values][:10]

    def make_slice(self, value):
        return self.slice_class(self.variable.name, value, self.values.index(value), self.is_dimension, self.is_info)

    def __repr__(self):
        return "%s[name=%s,values=%s]" % (self.__class__.__name__, self.variable.name, len(self.values))


class TimeCoordinate(Coordinate):
    slice_class = TimeSlice
    is_dimension = True
    convert = as_datetime


class LevelCoordinate(Coordinate):
    # This class is just in case we want to specialise
    # 'level', othewise, it is the same as OtherCoordinate
    slice_class = Slice
    is_dimension = False
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

        self.name = self.variable

        # if level:
        #     self.name += '_' + str(level)

        self.title = getattr(ds[self.variable], 'long_name',
                             getattr(ds[self.variable], 'standard_name',
                                     self.variable))

        # if level:
        #     self.title += ' @ ' + str(level)

        self.time = None

        for s in self.slices:

            if isinstance(s, TimeSlice):
                self.time = s.value

            if s.is_info:
                self.title += ' (' + s.name + '=' + str(s.value) + ')'

        key = 'style.netcdf.%s' % (self.name, )

        # Optimisation
        self.styles = context.stash.get(key)
        if self.styles is None:
            self.styles = context.stash[key] = context.styler.netcdf_styles(self, ds[variable], path, variable)

    def render(self, context, driver, style, legend={}):

        dimensions = ["%s:%s" % (s.name, s.index) for s in self.slices]
        data = []

        if dimensions:
            params = dict(netcdf_filename=self.path,
                          netcdf_value_variable=self.variable,
                          netcdf_dimension_setting=dimensions,
                          netcdf_dimension_setting_method='index')
        else:
            params = dict(netcdf_filename=self.path,
                          netcdf_value_variable=self.variable)

        # params['netcdf_field_automatic_scaling'] = 'off'

        if style:
            style.adjust_netcdf_plotting(params)

        data.append(driver.mnetcdf(**params))
        data.append(context.styler.contours(self, driver, style, legend))

        return data

    def __repr__(self):
        return "NetCDFField[%r,%r]" % (self.variable, self.slices)

    def as_dict(self):
        return dict(_class=self.__class__.__module__ + '.' + self.__class__.__name__,
                    name=self.name,
                    title=self.title,
                    path=self.path,
                    variable=self.variable,
                    slices=[s.as_dict() for s in self.slices],
                    styles=[s.as_dict() for s in self.styles],
                    time=self.time.isoformat() if self.time is not None else None)


class NetCDFReader:

    """Get WMS layers from a NetCDF file."""

    log = logging.getLogger(__name__)

    def __init__(self, context, path):
        self.path = path
        self.context = context

    def get_fields(self):
        with closing(xr.open_mfdataset(self.path)) as ds:
            return self._get_fields(ds)

    def _get_fields(self, ds):
        # Select only geographical variables

        self.log.info('Scanning file ===> : %s (size=%s)', self.path, os.path.getsize(self.path))

        fields = []

        skip = set()

        for name in ds.data_vars:
            v = ds[name]
            skip.update([c for c in getattr(v, 'coordinates', '').split(' ')])
            skip.update([c for c in getattr(v, 'bounds', '').split(' ')])

        for name in ds.data_vars:

            if name in skip:
                continue

            v = ds[name]

            coordinates = []

            # self.log.info('Scanning file: %s var=%s coords=%s', self.path, name, v.coords)

            info = [value for value in v.coords if value not in v.dims]

            for coord in v.coords:
                c = ds[coord]

                # self.log.info("COORD %s %s %s %s", coord, type(coord), hasattr(c, 'calendar'), c)

                standard_name = getattr(c, 'standard_name', None)
                axis = getattr(c, 'axis', None)
                long_name = getattr(c, 'long_name', None)

                use = False

                if standard_name in ('longitude', 'projection_x_coordinate') or (long_name == 'longitude'):
                    has_lon = True
                    use = True

                if standard_name in ('latitude', 'projection_y_coordinate') or (long_name == 'latitude'):
                    has_lat = True
                    use = True

                # Of course, not every one sets the standard_name
                if standard_name in ('time', 'forecast_reference_time') or axis == 'T':
                    coordinates.append(TimeCoordinate(c, coord in info))
                    use = True

                # TODO: Support other level types
                if standard_name in ('air_pressure', 'model_level_number', 'altitude'):  # or axis == 'Z':
                    coordinates.append(LevelCoordinate(c, coord in info))
                    use = True

                if not use:
                    coordinates.append(OtherCoordinate(c, coord in info))

            if not (has_lat and has_lon):
                self.log.info("NetCDFReader: skip %s (Not a 2 field)", name)
                continue

            for values in product(*[c.values for c in coordinates]):
                

                slices = []
                for value, coordinate in zip(values, coordinates):
                    
                    slices.append(coordinate.make_slice(value))

                fields.append(NetCDFField(self.context, self.path, ds, name, slices))

        if not fields:
            raise Exception("NetCDFReader no 2D fields found in %s", self.path)

        self.log.info('Scanning file <=== : %s (fields=%s)', self.path, len(fields))

        return fields
