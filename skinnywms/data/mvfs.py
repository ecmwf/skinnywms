# (C) Copyright 2012-2019 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation nor
# does it submit to any jurisdiction.

import logging
import yaml
from skinnywms import datatypes, errors
from skinnywms.fields.mvfield import MvField

__all__ = [
    'MvAvailability'
]

logging.basicConfig(level=logging.DEBUG)


class MvLayer(datatypes.Layer):
    def __init__(self, loader, name, title, zindex, conf):
        super().__init__(name, title, zindex)
        self._mvtype = conf.get('type')
        assert(self._mvtype is not None)
        self.loader = loader
        self.style_version = 0
        self.load_style(conf)
        self.style_version = conf.get('style_version', 0)

    def load_style(self, conf):
        self.style_version = conf.get('style_version', 0)

        # styles - aka visdefs
        style_conf_lst = []
        for style_conf in conf.get('styles'):
            style_verb = style_conf.get('_verb')
            if not style_verb:
                raise Exception('No _verb is specified for [%s] in style: %s' %
                                (self, style_conf))
            style_conf.pop('_verb')
            style_conf_lst.append(
                datatypes.StyleConfig(style_verb, style_conf))

        self._styles = [datatypes.Style('default', config=style_conf_lst)]

    def style(self, name):
        if len(self._styles) > 0:
            # Here name is the style name as requested in the GetMap request. 
            # It should be the version (an int) of the style. If it does not
            # match the stored style version we reload the style from the config
            # file!
            if name and int(name) != self.style_version:
                self.loader.load_style(self) 
                # now the style has been reloaded. If the style version 
                # still does not match we do not use the style at all!
                if int(name) != self.style_version:
                    raise errors.StyleNotDefined(name)

        if len(self._styles) > 0 and self._styles[0]:
            return self._styles[0]
        else:
            raise errors.StyleNotDefined(name)



class MvMapLayer(MvLayer):
    log = logging.getLogger(__name__)

    def __init__(self, loader, context, name, title, zindex, conf):
        super().__init__(loader, name, title, zindex, conf)
        assert(self._mvtype == 'map')

    # A static layer always returns itself for any given dimensions 
    # since it has no fields!'
    def select(self, dims):
        return self

    def render(self, context, driver, style, legend={}):
        data = []
        if style:
            # we apply all the configs
            for style_item in style.config:
                # self.log.info("style_config={}".format(style_item.as_dict()))
                data.append(driver.mcoast(style_item.config))
        return data

    @property
    def fixed_layer(self):
        return True

    @property
    def dimensions(self):
        return []

    @property
    def styles(self):
        return self._styles

    def as_dict(self):
        return dict(_class=self.__class__.__module__ + '.' +
                    self.__class__.__name__,
                    styles=[s.as_dict() for s in self._styles])


class MvDataLayer(MvLayer):
    log = logging.getLogger(__name__)

    def __init__(self, loader, context, name, title, zindex, conf):
        super().__init__(loader, name, title, zindex, conf)
        self.conf = conf
        index = conf.get('index')
        if type(index) == int:
            index = [index]
        elif type(index) != list or len(index) == 0:
            raise Exception('No index is specified for %s' % (self))

        path = conf.get('path')
        if not path:
            raise Exception('No path is specified for %s' % (self))

        self._mvtype = conf.get('type')
        if not self._mvtype:
            raise Exception('No type is specified for %s' % (self))

        # fields
        self._fields = {}
        self._first = None
        for i, idx in enumerate(index):
            self.add_field(MvField.make(self._mvtype)(self, context, path, i, idx))

    def add_field(self, field):
        # Cannot have a mix of None and ints
        assert field.index is not None
        assert isinstance(field.index, int)

        if field.index in self._fields:
            raise Exception("Duplicate index {} in  ({}, {})".format(
                field.index, self, field, self._fields[field.index]))

        self._fields[field.index] = field
        if not self._first:
            self._first = field

    @property
    def fixed_layer(self):
        return len(self._fields) == 0

    @property
    def dimensions(self):
        if self.fixed_layer:
            return []
        else:
            return [datatypes.Dimension('dim_index', 'no', 0, '0/{}/1'.
                                        format(len(self._fields) - 1))]

    @property
    def styles(self):
        return self._first.styles

    def __repr__(self):
        return "MvDataLayer[%s]" % (self.name,)

    # Returns the matching field object for the given dimensions
    def select(self, dims):
        if self.fixed_layer:
            return self

        index = dims.get("dim_index")
        # self.log.info("Look up layer with {} and dim_index {} (%s)".
        #              format(self, index, type(index)))

        if index is None:
            field = self._first
        else:
            field = self._fields[int(index)]
        return field

    def as_dict(self):
        return dict(_class=self.__class__.__module__ + '.' +
                    self.__class__.__name__,
                    fields=[field.as_dict()
                            for _, field in sorted(self._fields.items())])


# Define the availability when each field in a layer is accessed by its
# index in a file. In this case each field in a given layer must have a unique
# time. And obviously animation works on time.
class MvAvailability(datatypes.Availability):
    log = logging.getLogger(__name__)

    def __init__(self, path, *args, **kwargs):
        super().__init__(*args, auto_add_plotter_layers=False, **kwargs)
        self._path = path
        self._paths = {}

    def load(self):
        try:
            with open(self._path, 'rt') as f:
                conf = yaml.safe_load(f)
                layer_id = 0
                for conf_def in conf.get('layers'):
                    layer = conf_def.get('layer', None)
                    if layer:
                        self.add_layer(layer_id, layer)
                        layer_id += 1
                    else:
                        raise Exception(
                            'No layer defined in conf={}'.format(conf_def))

                # self.log.info('layers {}'.format(self._layers))
        except IOError as e:
            raise('Could not open config file: {}. Error: {}'.format(
                self._path, e))

    def add_layer(self, layer_id, conf):
        layer_type = conf.get('type')
        layer_name = conf.get('name')
        style_version = conf.get('style_version', 0)

        if not layer_type:
            raise Exception('No type is specified for layer in conf={}'.
                            format(conf))

        if not layer_name:
            layer_name = layer_type + "_" + str(layer_id)

        zindex = layer_id

        if layer_type == 'map':
            self._layers[layer_name] = MvMapLayer(self,
                self.context, layer_name, layer_name, zindex, conf)
        else:
            self._layers[layer_name] = MvDataLayer(self,
                self.context, layer_name, layer_name, zindex, conf)

    # Load style from the yaml config file for the given layer
    def load_style(self, layer):
        try:
            with open(self._path, 'rt') as f:
                conf = yaml.safe_load(f)
                for conf_def in conf.get('layers'):
                    conf_layer = conf_def.get('layer', None)
                    if conf_layer and conf_layer.get('name','') == layer.name:                       
                        layer.load_style(conf_layer)                 
        except IOError as e:
            raise('Could not open config file: {}. Error: {}'.format(
                self._path, e))
    
    # Load a layer from the yaml config file
    def load_layer(self, name):
        try:
            with open(self._path, 'rt') as f:
                conf = yaml.safe_load(f)
                for conf_def in conf.get('layers'):
                    layer = conf_def.get('layer', None)
                    if layer and layer.get('name','') == name:                       
                        layer_id = len(self._layers) + 1
                        self.add_layer(layer_id, layer)             
        except IOError as e:
            raise('Could not open config file: {}. Error: {}'.format(
                self._path, e))

    def add_file(self, path):
        pass

    def add_field(self, field):
        pass

    def layer(self, name, dims):
        try:
            return super().layer(name, dims)
        except errors.LayerNotDefined:    
            self.load_layer(name)
        
        return super().layer(name, dims)

    def as_dict(self):
        d = super().as_dict()
        d.update({'paths': self._paths})
        return d
