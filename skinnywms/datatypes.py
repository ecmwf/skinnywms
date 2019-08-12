# (C) Copyright 2012-2019 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation nor
# does it submit to any jurisdiction.

import datetime
import logging
from skinnywms import errors
import weakref

__all__ = [
    'Availability',
    'CRS',
    'Layer',
    'Plotter',
    'Style',
]

LOG = logging.getLogger(__name__)


class CRS:

    def __init__(self, name, n_lat, s_lat, w_lon, e_lon):
        self.name = name
        self.n_lat = n_lat
        self.s_lat = s_lat
        self.w_lon = w_lon
        self.e_lon = e_lon


class Style:

    def __init__(self, name, title=None, description=None, legend=None):
        self.name = name
        self.title = title is not None and title or name
        self.description = description is not None and description or name

    def as_dict(self):
        return dict(_class=self.__class__.__module__ + '.' + self.__class__.__name__,
                    name=self.name,
                    title=self.title,
                    description=self.description)

    def adjust_netcdf_plotting(self, params):
        pass

    def adjust_grib_plotting(self, params):
        pass


class Field:

    def style(self, name):

        if name == '':
            if self.styles:
                return self.styles[0]
            else:
                return None

        for s in self.styles:
            if s.name == name:
                return s

        raise errors.StyleNotDefined(name)


class Layer:

    def __init__(self, name, title, zindex=0, description=None, keywords=[]):
        self.name = name
        self.title = title
        self.description = description
        self.zindex = zindex


class Dimension:

    def __init__(self, name, units, default, extent):
        self.name = name
        self.units = units
        self.default = default
        self.extent = extent


class TimeDimension:

    def __init__(self, times, time_unit='hours'):

        times = sorted(times)

        self.name = 'time'
        self.units = 'ISO8601'
        self.default = times[0].isoformat() + 'Z'

        extent = []
        last_step = None
        last_iso = None

        prev = times[0]

        def step_diff(date1, date2, seconds):
            step = date1 - date2
            return step.days * 24 + step.seconds / seconds

        if time_unit == 'hours':
            seconds = 3600
            unit = 'H'

        if time_unit == 'minutes':
            seconds = 60
            unit = 'M'

        for time in times:
            iso = time.isoformat() + 'Z'

            step = step_diff(time, prev, seconds)
            prev = time
            if step == last_step:
                extent[-1] = '/'.join([last_iso, iso, 'PT%d%s' % (step, unit)])
            else:
                extent.append(iso)
                last_step = step
                last_iso = iso

        self.extent = ','.join(extent)


class DataLayer(Layer):

    # TODO: check the time-zone of the dates....

    def __init__(self, field):
        super(DataLayer, self).__init__(field.name, field.title)
        assert field.time is None or isinstance(field.time, datetime.datetime)
        self._first = field
        self._fields = {field.time: field}

    def add_field(self, field):
        assert self.name == field.name

        if self.title != field.title:
            raise Exception("Title redefined for %s [%s] => [%s]" % (self, self.title, field.title))

        # Cannot have a mix of None and Dates
        assert field.time is not None
        assert isinstance(field.time, datetime.datetime)

        if field.time in self._fields:
            LOG.info("Duplicate date %s in %s (%s, %s)" % (field.time, self, field, self._fields[field.time]))
            # return
            # Why are we sometimes throwing this exception .. : need to be checked
            raise Exception("Duplicate date %s in %s (%s, %s)" % (field.time, self, field, self._fields[field.time]))

        self._fields[field.time] = field

    @property
    def fixed_layer(self):
        return self._first.time is None

    @property
    def dimensions(self):
        if self.fixed_layer:
            return []
        else:
            return [TimeDimension(self._fields.keys())]

    @property
    def styles(self):
        # Assumes all styles shared
        return self._first.styles

    def __repr__(self):
        return "DataLayer[%s]" % (self.name,)

    def select(self, time):
        # TODO: select on more dimensions
        LOG.info("Look up layer with %s and time %s (%s)" % (self, time, type(time)))
        if time is None:
            field = self._first
        else:
            time = datetime.datetime.strptime(time[:19], "%Y-%m-%dT%H:%M:%S")
            field = self._fields[time]
        return field

    def as_dict(self):
        return dict(_class=self.__class__.__module__ + '.' + self.__class__.__name__,
                    fields=[field.as_dict() for _, field in sorted(self._fields.items())])


class Availability:

    def __init__(self):
        self._context = None
        self._layers = {}
        self._aliases = {}

    @property
    def context(self):
        return self._context()

    # @property.setter
    def set_context(self, context):
        self._context = weakref.ref(context)

    def add_field(self, field):
        # TODO: Use config....
        if not self._layers:
            self._aliases['default'] = field.name

        if field.name in self._layers:
            self._layers[field.name].add_field(field)
        else:
            self._layers[field.name] = DataLayer(field)

    def layers(self):
        if not self._layers:
            self.load()
        # TODO: Sort
        return [l for l in self._layers.values()]

    def layer(self, name, time):
        if not self._layers:
            self.load()

        LOG.info("Look up layer with name %s and time %s", name, time)

        while name in self._aliases:
            name = self._aliases[name]

        if name not in self._layers:
            raise errors.LayerNotDefined("Unknown layer '{}'".format(name))

        # TODO: select on othe dimenstions as well
        return self._layers[name].select(time=time)

    def as_dict(self):
        if not self._layers:
            self.load()
        return dict(_class=self.__class__.__module__ + '.' + self.__class__.__name__,
                    aliases=self._aliases,
                    layers=[layer.as_dict() for layer in self._layers.values()])


class Plotter:

    @property
    def context(self):
        return self._context()

    # @property.setter
    def set_context(self, context):
        self._context = weakref.ref(context)

    def layers(self):
        raise NotImplementedError

    @property
    def supported_crss(self):
        raise NotImplementedError

    @property
    def geographic_bounding_box(self):
        raise NotImplementedError

    def plot(self,
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
             transparent=None):
        raise NotImplementedError


class Styler:

    @property
    def context(self):
        return self._context()

    # @property.setter
    def set_context(self, context):
        self._context = weakref.ref(context)
