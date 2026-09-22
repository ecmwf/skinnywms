import datetime
import logging
import weakref
from abc import ABC, abstractmethod
from typing import Dict, List

from dateutil import parser

from skinnywms import errors
from skinnywms.server import WMSServer

# (C) Copyright 2012-2019 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation nor
# does it submit to any jurisdiction.


__all__ = [
    "Availability",
    "CRS",
    "Layer",
    "Plotter",
    "Style",
]

LOG = logging.getLogger(__name__)


def _parse_time(value) -> datetime.datetime:
    """Parses a WMS dimension value into a UTC datetime.

    :param value: an ISO 8601 timestamp, e.g. '2019-01-01T12:00:00Z'
    :return: the parsed time, in UTC
    :rtype: datetime.datetime
    """
    try:
        return datetime.datetime.strptime(
            str(value)[:19], "%Y-%m-%dT%H:%M:%S"
        ).replace(tzinfo=datetime.timezone.utc)
    except Exception:
        return parser.parse(str(value)[:19]).replace(tzinfo=datetime.timezone.utc)


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
            config=[s.as_dict() for s in self.config] if self.config else None,
        )

    def adjust_netcdf_plotting(self, params):
        pass

    def adjust_grib_plotting(self, params):
        pass


class Field:
    def style(self, name: str) -> str:

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
    def name(self, value: str) -> None:
        self._name = value

    @property
    def group_name(self) -> str:
        if self._group_name:
            return self._group_name
        else:
            return self.name  # fallback to name if unset

    @group_name.setter
    def group_name(self, value: str) -> None:
        self._group_name = value

    @property
    def title(self) -> str:
        if self._title:
            return self._title
        else:
            return "undefined"

    @title.setter
    def title(self, value: str) -> None:
        self._title = value

    @property
    def group_title(self) -> str:
        if self._group_title:
            return self._group_title
        else:
            return self.title  # fallback to title if unset

    @group_title.setter
    def group_title(self, value: str) -> None:
        self._group_title = value

    @property
    def companion(self) -> 'Field':
        if self._companion:
            return self._companion
        else:
            return None

    @companion.setter
    def companion(self, value: 'Field') -> 'Field':
        self._companion = value

    @property
    def reference_time(self) -> datetime.datetime:
        """The time at which the forecast was initialised (the 'forecast run'),
        or None for data that carries no such notion.

        :return: the forecast reference time, in UTC, or None
        :rtype: datetime.datetime
        """
        return getattr(self, "_reference_time", None)

    @reference_time.setter
    def reference_time(self, value: datetime.datetime) -> None:
        self._reference_time = value


class FieldReader(ABC):
    """Get WMS layers (fields) from a file."""

    def __init__(self, context: WMSServer, path: str) -> None:
        self._context = context
        self._path = path

    @property
    def context(self) -> WMSServer:
        return self._context

    @context.setter
    def context(self, context: WMSServer) -> None:
        self._context = weakref.ref(context)

    @property
    def path(self) -> str:
        return self._path

    @path.setter
    def path(self, path: str) -> None:
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
    def __init__(
        self,
        name: str,
        title: str,
        zindex: int = 0,
        description: str = None,
        keywords: List[str] = [],
    ):
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
    def __init__(
        self, name: str, units: str, default: str, extent: str, unitSymbol: str
    ):
        self.name = name
        self.units = units
        self.default = default
        self.extent = extent
        self.unitSymbol = unitSymbol

    def add_field(self, field: Field) -> None:
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

    def __repr__(self) -> str:
        return "%s[%s,%s,%s,%s,%s]" % (
            self.__class__,
            self.name,
            self.units,
            self.unitSymbol,
            self.default,
            self.extent,
        )


class TimeDimension(Dimension):
    def __init__(self, times: List[datetime.datetime]):
        super(TimeDimension, self).__init__(
            name="time", units="ISO8601", default=None, extent="", unitSymbol=None
        )
        times = sorted(
            [time.astimezone(tz=datetime.timezone.utc) for time in times]
        )  # convert all times to utc
        self.default = TimeDimension.format_time(times[0])

        self.extent = TimeDimension.format_extent(times)

    def equals(time1: datetime.datetime, time2: datetime.datetime) -> bool:
        if time1 is None and time2 is None:
            return True
        elif time1 is None or time2 is None:
            return False
        else:
            return (
                abs(
                    (
                        time1.astimezone(tz=datetime.timezone.utc)
                        - time2.astimezone(tz=datetime.timezone.utc)
                    ).total_seconds()
                )
                < 1
            )

    def format_time(time: datetime.datetime) -> str:
        return (
            time.astimezone(tz=datetime.timezone.utc).isoformat().replace(
                "+00:00", "Z")
        )

    def format_extent(times: List[datetime.datetime]) -> str:
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
            iso_ts = TimeDimension.format_time(time)

            delta = time - prev_time
            prev_time = time
            if delta == last_delta and delta != datetime.timedelta(0):
                extent[-1] = "/".join(
                    [last_iso_ts, iso_ts,
                        TimeDimension.format_iso_8601_duration(delta)]
                )
            else:
                extent.append(iso_ts)
                last_delta = delta
                last_iso_ts = iso_ts

        return ",".join(extent)

    def format_iso_8601_duration(period: datetime.timedelta) -> str:
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
            return ret  # no seconds or microseconds in this period

        remainder_s = period.seconds
        if remainder_s >= 3600:
            ret += "%dH" % (remainder_s / 3600)  # extract whole hours
            remainder_s = remainder_s % 3600

        if remainder_s >= 60:
            ret += "%dM" % (remainder_s / 60)  # extract whole minutes
            remainder_s = remainder_s % 60

        if remainder_s > 0 and period.microseconds == 0:
            ret += "%dS" % remainder_s  # only whole seconds
        elif period.microseconds > 0:
            ret += "%fS" % (
                remainder_s + period.microseconds / 1000000
            )  # floating point number
        return ret


class ReferenceTimeDimension(TimeDimension):
    """The forecast reference time dimension, i.e. the time at which the forecast
    was initialised (the 'forecast run'), as described in
    https://external.ogc.org/twiki_public/pub/MetOceanDWG/MetOceanWMSBPOnGoingDrafts/12-111r1_Best_Practices_for_WMS_with_Time_or_Elevation_dependent_data.pdf

    <Dimension name="reference_time" units="ISO8601" default="2019-01-02T00:00:00Z" multipleValues="0" nearestValue="0">2019-01-01T00:00:00Z,2019-01-02T00:00:00Z</Dimension>

    Clients request a value for it with the DIM_REFERENCE_TIME parameter.
    """

    def __init__(self, times: List[datetime.datetime]):
        super(ReferenceTimeDimension, self).__init__(times)
        self.name = "reference_time"
        # unlike for the validity time, the most useful default run is the latest
        self.default = TimeDimension.format_time(max(times))


class ElevationDimension(Dimension):
    """An elevation dimension representing vertical 'levels' as described in
    https://external.ogc.org/twiki_public/pub/MetOceanDWG/MetOceanWMSBPOnGoingDrafts/12-111r1_Best_Practices_for_WMS_with_Time_or_Elevation_dependent_data.pdf

    Most common cases:

    1) Numeric elevation values, e.g isobaric (pressure) levels in [hPa] or isometric levels in [m]
    <Dimension name="elevation" units="hectoPascal" unitSymbol="hPa" default="1000" multipleValues="0" nearestValue="0" current="0">100,200,500,1000</Dimension>

    2) Named surfaces
    <Dimension name="elevation" units="computed_surface" unitSymbol="" default="0" multipleValues="0" nearestValue="0" current="0">1/90/1</Dimension>
    """

    def __init__(
        self,
        levels: List[str],
        default: str,
        units: str = "computed_surface",
        unitSymbol: str = "",
    ):
        super(ElevationDimension, self).__init__(
            name="elevation",
            units=units,
            default=default,
            extent=",".join(levels),
            unitSymbol=unitSymbol,
        )

        if self.default is None and len(levels) > 0:
            self.default = levels[0]

        # TODO: process list of levels to fill extent
        # ...

    def add_field(self, field: Field) -> None:
        pass


class DataLayer(Layer):

    # TODO: check the time-zone of the dates....

    def __init__(
        self,
        field: Field,
        group_dimensions: bool = False,
        reference_time_dimension: bool = False,
    ) -> None:
        self._group_dimensions = group_dimensions
        self._reference_time_dimension = reference_time_dimension
        if self._group_dimensions:
            super(DataLayer, self).__init__(
                field.group_name, field.group_title)
        else:
            super(DataLayer, self).__init__(field.name, field.title)
        self._first = field

        self._fields = {self._key(field): field}

        self._time_dimension_is_none = field.time is None
        self._times = None

    def _key(self, field: Field) -> tuple:
        """Builds the key under which a field is stored, i.e. the combination of
        dimension values that identifies it within this layer.

        Unless the reference time dimension is enabled, the forecast reference time
        is left out of the key, so that fields from different forecast runs sharing
        a validity time and elevation overwrite one another, as they always have.

        :param field: the field to build a key for
        :type field: Field
        :return: the (reference_time, time, elevation) key
        :rtype: tuple
        """
        assert field.time is None or (
            isinstance(field.time, datetime.datetime)
            and field.time == field.time.astimezone(tz=datetime.timezone.utc)
        )
        assert field.levelist is None or isinstance(field.levelist, int)

        reference_time = (
            field.reference_time if self._reference_time_dimension else None
        )

        return (reference_time, field.time, field.levelist)

    @property
    def reference_time_dimension(self) -> bool:
        """If set to 'True', fields are additionally keyed on the forecast reference
        time, and layers holding more than one forecast run advertise a
        'reference_time' dimension.

        :return: 'True' if the reference time dimension is enabled, else 'False'
        :rtype: bool
        """
        return self._reference_time_dimension

    def select_nearest_available_time(
        self, time: datetime.datetime, reference_time: datetime.datetime = None
    ) -> datetime.datetime:
        """Selects the nearest available time less than or equal to 'time'.
            If time is None, the earliest available time is returned.

        Args:
            time (datetime.datetime): the time
            reference_time (datetime.datetime): if given, only times belonging to
                that forecast run are considered

        Returns:
            datetime.datetime: the nearest available time less than or equal to 'time'
        """
        nearest_time = None
        for atime in self.available_times(reference_time=reference_time):
            if time is None:
                return atime

            if atime <= time:
                nearest_time = atime
            else:
                return nearest_time
        return nearest_time

    def select_nearest_available_reference_time(
        self, reference_time: datetime.datetime
    ) -> datetime.datetime:
        """Selects the nearest available reference time less than or equal to
            'reference_time', i.e. never a more recent forecast run than the one
            requested. If 'reference_time' is None, or predates every available
            run, the latest available run is returned, which is also the one
            advertised as the dimension default.

        Args:
            reference_time (datetime.datetime): the requested forecast run

        Returns:
            datetime.datetime: the selected reference time, or None if this layer
                has no reference time at all
        """
        available = self.available_reference_times()
        if len(available) < 1:
            return None

        if reference_time is None:
            return available[-1]

        nearest_reference_time = None
        for aref in available:
            if aref <= reference_time:
                nearest_reference_time = aref
            else:
                break

        if nearest_reference_time is None:
            # the requested run predates everything we hold, fall back to the default
            return available[-1]

        return nearest_reference_time

    def available_reference_times(self) -> List[datetime.datetime]:
        """Returns a sorted list of all available forecast reference times. Returns an
        empty list, if no reference time dimension is available.

        Returns:
            List[datetime.datetime]: a sorted list of all available reference times
        """
        reference_times = sorted(
            {l[0] for l in self._fields.keys() if l[0] is not None}
        )
        return reference_times

    def available_times(
        self, reference_time: datetime.datetime = None
    ) -> List[datetime.datetime]:
        """Returns a sorted list of all available times. Returns an empty list, if no time dimension is available.

        Args:
            reference_time (datetime.datetime): if given, only the times belonging to
                that forecast run are returned

        Returns:
            List[datetime.datetime]: a sorted list of all available times
        """
        times = sorted(
            {
                l[1]
                for l in self._fields.keys()
                if l[1] is not None
                and (
                    reference_time is None
                    or TimeDimension.equals(l[0], reference_time)
                )
            }
        )
        return times

    def available_elevations(
        self, reference_time: datetime.datetime = None
    ) -> List[int]:
        """Return a sorted list of all available elevations. Returns an empty list, if no elevation dimension is available.

        Args:
            reference_time (datetime.datetime): if given, only the elevations belonging
                to that forecast run are returned

        Returns:
            List[int]: a sorted list of all available elevations
        """
        elevations = sorted(
            {
                str(l[2])
                for l in self._fields.keys()
                if l[2] is not None
                and (
                    reference_time is None
                    or TimeDimension.equals(l[0], reference_time)
                )
            }
        )
        return elevations

    def valid_elevations(
        self, reference_time: datetime.datetime, time: datetime.datetime
    ) -> set:
        """Returns the set of elevations available for a given forecast run and
            validity time. Unlike 'available_elevations' this keeps the elevations
            as stored, i.e. as ints or None, so that they can be used to build a
            field key.

        Args:
            reference_time (datetime.datetime): the forecast run
            time (datetime.datetime): the validity time

        Returns:
            set: the elevations available for that combination
        """
        return {
            l[2]
            for l in self._fields.keys()
            if TimeDimension.equals(l[0], reference_time)
            and TimeDimension.equals(l[1], time)
        }

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
                    "Title redefined for %s [%s] => [%s]"
                    % (self, self.title, field.group_title)
                )

        else:  # don't group levels
            assert self.name == field.name

            if self.title != field.title:
                raise Exception(
                    "Title redefined for %s [%s] => [%s]"
                    % (self, self.title, field.title)
                )

        # Cannot have a mix of None and Dates
        assert (
            field.time is None
            and self._time_dimension_is_none
            or (
                isinstance(field.time, datetime.datetime)
                and not self._time_dimension_is_none
                and field.time == field.time.astimezone(tz=datetime.timezone.utc)
            )
        )

        key = self._key(field)

        if key in self._fields:
            LOG.info(
                "Duplicate field (reference time: %s, time: %s, elevation: %s) in %s (%s, %s)"
                % (key[0], key[1], key[2], self, field, self._fields[key])
            )

            # # Why are we sometimes throwing this exception .. : need to be checked
            # raise Exception(
            #     "Duplicate date %s in %s (%s, %s)"
            #     % (field.time, self, field, self._fields[field.time])
            # )

        self._fields[key] = field

    @property
    def fixed_layer(self) -> bool:
        return self._first.time is None and self._first.levelist is None

    @property
    def dimensions(self) -> List[Dimension]:
        dims = []
        if not self.fixed_layer:
            reference_times = self.available_reference_times()
            if len(reference_times) > 1:
                # a single forecast run needs no dimension to select it, and
                # advertising one would change the capabilities of every
                # single-run dataset
                dims.append(ReferenceTimeDimension(reference_times))
            times = self.available_times()
            if len(times) > 0:
                dims.append(TimeDimension(times))
            elevations = self.available_elevations()
            if len(elevations) > 0:
                elev_units = "computed_surface"
                unit_symbol = ""
                if self._first.levtype == "pl":
                    # pressure levels, usually in hPa (GRIB)
                    # if it's NetCDF-CF compliant data, it's in Pa
                    # TODO: find out the actual units
                    elev_units = "hectoPascal"
                    unit_symbol = "hPa"

                elevdim = ElevationDimension(
                    levels=elevations,
                    units=elev_units,
                    default=elevations[0],
                    unitSymbol=unit_symbol,
                )
                dims.append(elevdim)
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

        time = dims.get("time", None)  # try get time string
        elevation = dims.get("elevation", None)  # try get elevation string
        # try get reference time (forecast run) string
        reference_time = dims.get("reference_time", None)
        LOG.info(
            "Look up layer with %s and reference time %s (%s) and time %s (%s) and elevation %s (%s)"
            % (
                self,
                reference_time,
                type(reference_time),
                time,
                type(time),
                elevation,
                type(elevation),
            )
        )

        # the forecast run is selected first, every other dimension is then
        # resolved within that run
        if len(self.available_reference_times()) > 0:
            if reference_time is not None:
                reference_time = _parse_time(reference_time)
            reference_time = self.select_nearest_available_reference_time(
                reference_time
            )
        elif reference_time is not None:
            # no reference time dimension was advertised for this layer, so
            # there is nothing to select
            LOG.info(
                "Ignoring reference time %s, %s has no reference time dimension"
                % (reference_time, self)
            )
            reference_time = None

        valid_elevations = {}
        if time is None:
            if reference_time is None or TimeDimension.equals(
                self._first.reference_time, reference_time
            ):
                # keep to the historical default: the first field that was scanned
                time = self._first.time
                valid_elevations = {self._first.levelist}
            else:
                # default to the earliest validity time of the requested run
                time = self.select_nearest_available_time(
                    None, reference_time=reference_time
                )
                valid_elevations = self.valid_elevations(reference_time, time)
        else:
            time = _parse_time(time)

            # check if the given time exists
            time = self.select_nearest_available_time(
                time, reference_time=reference_time
            )
            valid_elevations = self.valid_elevations(reference_time, time)
            if len(valid_elevations) < 1:
                raise KeyError(
                    "(%s,%s,%s) TIME not found. Available combinations: %s"
                    % (reference_time, time, elevation, self._fields.keys())
                )
                # selected time not found, fallback to a valid time
                # time = self._first.time
                valid_elevations = {self._first.levelist}

        if elevation is None:
            elevation = valid_elevations.pop()
        else:
            # parse int elevation
            elevation = int(elevation)
            if elevation not in valid_elevations:
                elevation = valid_elevations.pop()

        if (reference_time, time, elevation) not in self._fields.keys():
            raise KeyError(
                "(%s,%s,%s) not found. Available combinations: %s"
                % (reference_time, time, elevation, self._fields.keys())
            )

        return self._fields[(reference_time, time, elevation)]

    def as_dict(self):
        return dict(
            _class=self.__class__.__module__ + "." + self.__class__.__name__,
            fields=[field.as_dict()
                    for _, field in sorted(self._fields.items())],
        )


class Availability:
    def __init__(
        self,
        auto_add_plotter_layers: bool = True,
        group_dimensions: bool = False,
        reference_time_dimension: bool = False,
    ):
        self._context = None
        self._layers: Dict[str, DataLayer] = {}
        self._aliases = {}
        self._auto_add_plotter_layers = auto_add_plotter_layers
        self._group_dimensions = group_dimensions
        self._reference_time_dimension = reference_time_dimension

    @property
    def context(self) -> WMSServer:
        return self._context()

    # @context.setter
    def set_context(self, context: WMSServer):
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
    def reference_time_dimension(self) -> bool:
        """If set to 'True', fields are additionally keyed on the forecast reference
        time, so that several forecast runs can be served from the same layer, and
        layers holding more than one run advertise a 'reference_time' dimension.

        :return: 'True' if the reference time dimension is enabled, else 'False'
        :rtype: bool
        """
        return self._reference_time_dimension

    @property
    def auto_add_plotter_layers(self) -> bool:
        return self._auto_add_plotter_layers

    def add_field(self, field: Field) -> None:
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
                self._layers[field.group_name] = DataLayer(
                    field,
                    group_dimensions=self.group_dimensions,
                    reference_time_dimension=self.reference_time_dimension,
                )
        else:  # don't group dimensions
            if not self._layers:
                self._aliases["default"] = field.name

            if field.name in self._layers:
                # field with the same name already
                # exists, so try to group
                self._layers[field.name].add_field(field)
            else:
                self._layers[field.name] = DataLayer(
                    field,
                    group_dimensions=self.group_dimensions,
                    reference_time_dimension=self.reference_time_dimension,
                )

    def layers(self):
        if not self._layers:
            self.load()
        # return a sorted list
        ret = [l for l in self._layers.values()]
        ret.sort(key=lambda x: x.name, reverse=False)
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
    def set_context(self, context: WMSServer):
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
    def set_context(self, context: WMSServer):
        self._context = weakref.ref(context)
