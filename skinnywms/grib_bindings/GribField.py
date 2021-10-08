# (C) Copyright 2012-2019 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation nor
# does it submit to any jurisdiction.
#

import datetime
from typing import Dict
import numpy as np

from .bindings import grib_get_metadata, grib_handle_delete, grib_get, grib_values
from .bindings import (
    grib_get_keys_values,
    grib_get_gaussian_latitudes,
    grib_pl_array,
    grib_get_size,
    grib_get_code,
)


REGULAR_CACHE = {}
REDUCED_CACHE = {}


class Regular(object):
    def array(self, grib):
        # For now...
        assert grib.scanningMode == 0
        return grib.values.reshape((grib.Nj, grib.Ni))

    def coordinates(self, grib, coords, combine_order, attributes, dims):

        key = self.cache_key(grib)
        _coords, _attributes = REGULAR_CACHE.get(key, (None, None))

        if _coords is None:

            _coords = {}
            _attributes = {}

            _coords["latitude"] = self.latitudes(grib)
            _attributes["latitude"] = dict(
                long_name="Latitude", units="degrees_north", standard_name="latitude"
            )

            _coords["longitude"] = self.longitudes(grib)
            _attributes["longitude"] = dict(
                long_name="Longitude", units="degrees_east", standard_name="longitude"
            )

        REGULAR_CACHE[key] = (_coords, _attributes)

        coords.update(_coords)
        attributes.update(_attributes)

        dims.append("latitude")
        dims.append("longitude")


class RegularLL(Regular):
    def cache_key(self, grib):
        return (
            grib.numberOfDataPoints,
            grib.latitudeOfFirstGridPointInDegrees,
            grib.latitudeOfLastGridPointInDegrees,
            grib.Nj,
            grib.longitudeOfFirstGridPointInDegrees,
            grib.longitudeOfLastGridPointInDegrees,
            grib.Ni,
        )

    def latitudes(self, grib):
        assert grib.scanningMode == 0
        return np.linspace(
            grib.latitudeOfFirstGridPointInDegrees,
            grib.latitudeOfLastGridPointInDegrees,
            grib.Nj,
        )

    def longitudes(self, grib):
        assert grib.scanningMode == 0
        return np.linspace(
            grib.longitudeOfFirstGridPointInDegrees,
            grib.longitudeOfLastGridPointInDegrees,
            grib.Ni,
        )


class RegularGG(Regular):
    def cache_key(self, grib):
        return (
            grib.numberOfDataPoints,
            grib.latitudeOfFirstGridPointInDegrees,
            grib.latitudeOfLastGridPointInDegrees,
            grib.Nj,
            grib.longitudeOfFirstGridPointInDegrees,
            grib.longitudeOfLastGridPointInDegrees,
            grib.Ni,
            grib.N,
        )

    def latitudes(self, grib):
        assert grib.scanningMode == 0
        return grib_get_gaussian_latitudes(grib.N)

    def longitudes(self, grib):
        assert grib.scanningMode == 0
        return np.linspace(
            grib.longitudeOfFirstGridPointInDegrees,
            grib.longitudeOfLastGridPointInDegrees,
            grib.Ni,
        )


def reduced_grid(pl_array, latitudes):
    for pl, lat in zip(pl_array, latitudes):
        if pl == 0:
            continue

        for n in range(0, pl):
            lon = (360.0 * n) / pl
            yield lat, lon


class Reduced(object):
    def array(self, grib):
        assert grib.scanningMode == 0
        return grib.values.reshape((grib.numberOfDataPoints,))

    def coordinates(self, grib, coords, combine_order, attributes, dims):

        key = self.cache_key(grib)
        _coords, _attributes = REDUCED_CACHE.get(key, (None, None))

        if _coords is None:

            _coords = {}
            _attributes = {}

            # TODO: that may not be the fastest way...
            n = grib.numberOfDataPoints
            lats = np.ndarray((n,))
            lons = np.ndarray((n,))
            i = 0
            for lat, lon in reduced_grid(grib.pl_array, self.latitudes(grib)):
                lats[i] = lat
                lons[i] = lon
                i = i + 1

            _coords["latitude"] = ("rgrid", lats.reshape((n,)))
            _attributes["latitude"] = dict(
                long_name="Latitude", units="degrees_north", standard_name="latitude"
            )

            _coords["longitude"] = ("rgrid", lons.reshape((n,)))
            _attributes["longitude"] = dict(
                long_name="Longitude", units="degrees_east", standard_name="longitude"
            )

            """
            See http://cfconventions.org/cf-conventions/v1.6.0/cf-conventions.html#reduced-horizontal-grid
            Panoply can open these files. The values for latdim and londim seem irrelevant
            """
            londim = len(grib.pl_array)
            latdim = n // londim

            # We use rgrid:latdim and rgrid:londim to pass the information that will
            # be used when saving to netcdf

            _coords["rgrid"] = np.array(range(0, n))
            _attributes["rgrid"] = dict(
                compress="latdim londim", latdim=latdim, londim=londim
            )

            REDUCED_CACHE[key] = (_coords, _attributes)

        coords.update(_coords)
        attributes.update(_attributes)

        combine_order.append(("rgrid", 0))
        dims.append("rgrid")

    #     int rgrid(rgrid);
    # rgrid:compress = "latdim londim";

    # coords["y"] = range(0, n)
    # coords["x"] = [0]
    # print len(coords["rgrid"])
    # dims.append("lat")
    # dims.append("lon")


class ReducedLL(Reduced):
    def cache_key(self, grib):
        return (
            grib.numberOfDataPoints,
            grib.latitudeOfFirstGridPointInDegrees,
            grib.latitudeOfLastGridPointInDegrees,
            grib.Nj,
            grib.longitudeOfFirstGridPointInDegrees,
            grib.longitudeOfLastGridPointInDegrees,
            grib.Ni,
            grib.pl_array_size,
        )

    def latitudes(self, grib):
        assert grib.scanningMode == 0
        return np.linspace(
            grib.latitudeOfFirstGridPointInDegrees,
            grib.latitudeOfLastGridPointInDegrees,
            grib.Nj,
        )


class ReducedGG(Reduced):
    def cache_key(self, grib):
        return (
            grib.numberOfDataPoints,
            grib.latitudeOfFirstGridPointInDegrees,
            grib.latitudeOfLastGridPointInDegrees,
            grib.Nj,
            grib.longitudeOfFirstGridPointInDegrees,
            grib.longitudeOfFirstGridPointInDegrees,
            grib.longitudeOfLastGridPointInDegrees,
            grib.Ni,
            grib.pl_array_size,
            grib.N,
        )

    def latitudes(self, grib):
        assert grib.scanningMode == 0
        return grib_get_gaussian_latitudes(grib.N)


GRID_TYPES = {
    "regular_ll": RegularLL(),
    "regular_gg": RegularGG(),
    "reduced_ll": ReducedLL(),
    "reduced_gg": ReducedGG(),
    "rotated_ll": RegularLL(),  # For now, we do not  make use of this information .
    "lambert": RegularLL(),
}


class PressureLevel(object):
    def coordinates(self, grib, coords, combine_order, attributes, dims):
        level = float(grib.levelist)  # Some tools expect a float
        coords["level"] = level
        combine_order.append(("level", level))

        # TODO: what is the standard_name for pressure levels
        attributes["level"] = dict(
            units="hPa",
            long_name="Isobaric surface",
            standard_name="air_pressure",
            positive="down",
        )


class ModelLevel(object):
    def coordinates(self, grib, coords, combine_order, attributes, dims):
        level = float(grib.levelist)  # Some tools expect a float
        coords["level"] = level
        combine_order.append(("level", level))

        # TODO: may be atmosphere_hybrid_height_coordinate
        attributes["level"] = dict(
            units="1",
            standard_name="model_level_number",
            long_name="Model level",
            positive="down",
        )


class SingleLevel(object):
    def coordinates(self, grib, coords, combine_order, attributes, dims):
        pass


# Section 4 - Code Table 5 : Fixed surface types and units
# https://apps.ecmwf.int/codes/grib/format/grib2/ctables/4/5
LEVEL_TYPE_CODES = {
    1: SingleLevel(),  # 1 sfc Ground or water surface
    8: SingleLevel(),  # 8 sfc Nominal top of the atmosphere
    100: PressureLevel(),  # 100 pl Isobaric surface (Pa)
    102: SingleLevel(),  #  Specific altitude above mean sea level (m)
    103: SingleLevel(),  # 103 sfc Specified height level above ground (m)
    106: SingleLevel(),  # 106 sfc Depth below land surface (m)
    111: ModelLevel(),  # 111 ml Eta level
    150: ModelLevel(),  # 150 dwd model level
}

LEVEL_TYPES = {"pl": PressureLevel(), "sfc": SingleLevel(), "ml": ModelLevel()}


class GribField(object):
    def __init__(self, handle, path, offset):
        self._handle = handle

        self._path = path
        self._offset = offset

        # The function grib_handle_delete may be destroyed
        # before the object is garbage collected
        self._delete = grib_handle_delete

        self._values = None

        try:
            self._grid = GRID_TYPES[self.gridType]
        except KeyError:
            raise Exception(
                "Unsupported grid type '{}' in grib {}".format(self.gridType, path)
            )

        try:
            # try mapping by name
            if self.levtype in LEVEL_TYPES:
                self._levtype = LEVEL_TYPES[self.levtype]
            else:
                # try mapping by code
                levtype_code = self.get_code("levtype")
                self._levtype = LEVEL_TYPE_CODES[levtype_code]
        except KeyError:
            raise Exception(
                "Unsupported level type '{}' in grib {}".format(self.levtype, path)
            )

    @property
    def metadata(self) -> Dict[str,str]:
        return grib_get_metadata(self._handle)

    @property
    def byte_offset(self):
        return self._offset

    @property
    def values(self):
        if self._values is None:
            self._values = grib_values(self._handle)
        return self._values

    @property
    def array(self):
        return self._grid.array(self)

    @property
    def latitudes(self):
        return self._grid.latitudes(self)

    @property
    def longitudes(self):
        return self._grid.longitudes(self)

    @property
    def valid_date(self):
        step = self.step

        if isinstance(step, str):
            # It's a range, use end of range
            step = int(step.split("-")[-1])

        return self.base_date + self.get_timedelta(step)

    @property
    def base_date(self):
        date, time = self.date, self.time
        return datetime.datetime(
            date // 10000, (date % 10000) // 100, date % 100, time // 100, time % 100, 0
        )

    @property
    def mars_request(self):
        return grib_get_keys_values(self._handle, "mars")

    @property
    def pl_array(self):
        return grib_pl_array(self._handle)

    @property
    def pl_array_size(self):
        return grib_get_size(self._handle, "pl")

    def __del__(self):
        self._delete(self._handle)

    def __getitem__(self, name):
        try:
            return grib_get(self._handle, name)
        except Exception:
            raise KeyError(name)

    def __getattr__(self, name):
        try:
            return grib_get(self._handle, name)
        except Exception:
            raise AttributeError(name)

    def get(self, name):
        try:
            return grib_get(self._handle, name)
        except Exception:
            return None

    def get_code(self, name):
        return grib_get_code(self._handle, name)

    def get_timedelta(self, step):
        # see Section 4 - Code Table 4 : Indicator of unit of time range
        # https://apps.ecmwf.int/codes/grib/format/grib2/ctables/4/4
        if self.stepUnits == 0:
            # Minute
            return datetime.timedelta(minutes=step)
        elif self.stepUnits == 1:
            # Hour
            return datetime.timedelta(hours=step)
        elif self.stepUnits == 2:
            # Day
            return datetime.timedelta(days=step)
        elif self.stepUnits == 3:
            # Month
            return datetime.timedelta(months=step)
        elif self.stepUnits == 4:
            # Year
            return datetime.timedelta(years=step)
        elif self.stepUnits == 5:
            # Decade (10 years)
            return datetime.timedelta(years=10 * step)
        elif self.stepUnits == 6:
            # Normal (30 years)
            return datetime.timedelta(years=30 * step)
        elif self.stepUnits == 7:
            # Century (100 years)
            return datetime.timedelta(years=100 * step)
        # 8 - 9 Reserved
        elif self.stepUnits == 10:
            # 3 hours
            return datetime.timedelta(hours=3 * step)
        elif self.stepUnits == 11:
            # 6 hours
            return datetime.timedelta(hours=6 * step)
        elif self.stepUnits == 12:
            # 12 hours
            return datetime.timedelta(hours=12 * step)
        elif self.stepUnits == 13:
            # Second
            return datetime.timedelta(seconds=step)
        # 192-254 Reserved for local use
        elif self.stepUnits == 255:
            # Missing
            # fall back to hours
            return datetime.timedelta(hours=step)
        else:
            # fall back to hours
            return datetime.timedelta(hours=step)

    def coordinates(self, coords, combine_order, attributes, dims):

        coords["reftime"] = self.base_date
        combine_order.append(("reftime", self.base_date))
        attributes["reftime"] = dict(
            standard_name="forecast_reference_time", long_name="Forecast reference time"
        )

        # time, ensemble, level, latitude, longitude

        coords["time"] = self.valid_date
        combine_order.append(("time", self.valid_date))

        number = self.get("mars.number")
        if number is not None:
            coords["number"] = number
            combine_order.append(("number", number))
            attributes["number"] = dict(
                units="1", standard_name="realization", long_name="Ensemble number"
            )

        self._levtype.coordinates(self, coords, combine_order, attributes, dims)
        self._grid.coordinates(self, coords, combine_order, attributes, dims)
