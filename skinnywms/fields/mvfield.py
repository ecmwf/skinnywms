# (C) Copyright 2012-2019 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation nor
# does it submit to any jurisdiction.


from skinnywms import datatypes, errors
import logging


class MvField(datatypes.Field):
    log = logging.getLogger(__name__)

    def __init__(self, layer, context, path, index, data_index):
        self.path = path
        self.layer = layer
        self.index = index
        self.data_index = data_index
        self.time = self.index
        self.name = "METVIEW"
        self.title = "METVIEW"
        assert(layer)

    def style(self, name):
        return self.layer.style(name)
    
    @property
    def styles(self):
        return self.layer.styles

    def render_style(self, driver, style):
        data = []
        # we apply all the configs
        for style_item in style.config:
            # self.log.info("style_config={}".format(style.config))
            driver_method = getattr(driver, style_item.verb)
            data.append(driver_method(style_item.config))
        return data

    @staticmethod
    def make(field_type):
        if field_type in _makers:
            return _makers[field_type]
        else:
            raise ValueError('Unsupported field type {})'.format(field_type))

    def as_dict(self):
        raise NotImplementedError

    def __repr__(self):
        raise NotImplementedError


class MvGribField(MvField):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def render(self, context, driver, style, legend={}):
        data = []
        params = {'grib_input_file_name': self.path,
                  'grib_field_position': self.data_index}

        data.append(driver.mgrib(**params))
        # self.log.info('render style= {}', style.as_dict())
        data.extend(self.render_style(driver, style))
        return data

    def as_dict(self):
        return dict(_class=self.__class__.__module__ +
                    '.' + self.__class__.__name__,
                    name=self.name,
                    title=self.title,
                    path=self.path,
                    index=self.index,
                    data_index=self.data_index,
                    styles=[s.as_dict() for s in self.styles])

    def __repr__(self):
        return 'MvGribField[{},{},{}]'.format(
            self.path, self.index, self.data_index)


class MvGribVectorField(MvField):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def render(self, context, driver, style, legend={}):
        data = []
        params = {'grib_input_file_name': self.path,
                  'grib_wind_position1': self.data_index[0],
                  'grib_wind_position2': self.data_index[1]}

        data.append(driver.mgrib(**params))
        self.log.info('render style= {}', style.as_dict())
        data.extend(self.render_style(driver, style))
        return data

    def as_dict(self):
        return dict(_class=self.__class__.__module__ +
                    '.' + self.__class__.__name__,
                    name=self.name,
                    title=self.title,
                    path=self.path,
                    index=self.index,
                    data_index=self.data_index,
                    styles=[s.as_dict() for s in self.styles])

    def __repr__(self):
        return 'MvGribVectorField[{},{},{}]'.format(
            self.path, self.index, self.data_index)


class MvGeopointsField(MvField):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def render(self, context, driver, style, legend={}):
        data = []
        params = {'geo_input_file_name': self.path}

        data.append(driver.mgeo(**params))
        self.log.info('geopoints render style= {}', style.as_dict())
        data.extend(self.render_style(driver, style))
        return data

    def as_dict(self):
        return dict(_class=self.__class__.__module__ +
                    '.' + self.__class__.__name__,
                    name=self.name,
                    title=self.title,
                    path=self.path,
                    index=self.index,
                    data_index=self.data_index,  
                    styles=[s.as_dict() for s in self.styles])

    def __repr__(self):
        return 'MvGeopointsField[{},{},{}]'.format(
            self.path, self.index, self.data_index)


class MvGeopointsVectorField(MvField):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def render(self, context, driver, style, legend={}):
        data = []
        params = {'geo_input_file_name': self.path}

        data.append(driver.mgeo(**params))
        data.extend(self.render_style(driver, style))
        return data

    def as_dict(self):
        return dict(_class=self.__class__.__module__ +
                    '.' + self.__class__.__name__,
                    name=self.name,
                    title=self.title,
                    path=self.path,
                    index=self.index,
                    data_index=self.data_index,  
                    styles=[s.as_dict() for s in self.styles])

    def __repr__(self):
        return 'MvGeopointsField[{},{},{}]'.format(
            self.path, self.index, self.data_index)


_makers = {
        'grib': MvGribField,
        'grib_vector': MvGribField,
        'geopoints': MvGeopointsField,
        'geopoints_vector': MvGeopointsVectorField
    }
