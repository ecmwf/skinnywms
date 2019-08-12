# (C) Copyright 2012-2019 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation nor
# does it submit to any jurisdiction.

import logging
import mimetypes
import os
import threading
import pprint

from Magics import macro

from skinnywms import datatypes, errors


__all__ = [
    'Plotter',
]


mimetypes.add_type('application/x-grib', '.grib', strict=False)
mimetypes.add_type('application/x-netcdf', '.nc', strict=False)
mimetypes.add_type('application/x-netcdf', '.nc4', strict=False)


_CRSS = {crs['name']: datatypes.CRS(**crs) for crs in macro.wmscrs()['crss']}


MAGICS_OUTPUT_TYPES = {
    'image/png': 'png',
}
LOCK = threading.Lock()

MACRO_TEXT = """
{}

from Magics import macro

import os

try:
    import requests
except:
    requests = None

def download(url, path):

    if requests is None:
        return

    if os.path.exists(path):
        return

    print("Downloading url %s" % (url,))

    r = requests.get(url, stream=True, verify=False)
    r.raise_for_status()
    tmp = path + '.download'
    with open(tmp, 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024):
            f.write(chunk)

    os.rename(tmp, path)


args = []

{}

try:
    macro.plot(*args)
except Exception as e:
    print("Got exception in plot %s" % (e,))
    raise
"""


class StaticLayer(datatypes.Layer):

    def style(self, name):
        return None

    def render(self, context, driver, style):
        return [driver.mcoast(map_coastline_general_style=self.name,
                              map_coastline_resolution='medium')]

    def __repr__(self):
        return 'StaticLayer[%s]' % (self.name,)


class MagicsWebStyle(datatypes.Style):
    pass


class Plotter(datatypes.Plotter):

    supported_crss = tuple(_CRSS.values())

    geographic_bounding_box = macro.wmscrs()['geographic_bounding_box']

    log = logging.getLogger(__name__)



    def __init__(self, styles=None):
        if styles is None:
            styles = {}
        self._styles = styles
        self._layers = {
            layer.name: layer
            for layer in [
                StaticLayer('foreground', title='Foreground', zindex=99999),
                StaticLayer('background', title='Background', zindex=-99999),
                StaticLayer('grid', title='Grid', zindex=99999),
                StaticLayer('boundaries', title='Boundaries', zindex=99999),
            ]
        }

    def layers(self):
        for layer in self._layers.values():
            yield layer

    def layer(self, name, time=None):
        try:
            return self._layers[name]
        except KeyError:
            raise errors.LayerNotDefined("Unknown layer '{}'".format(name))

    def plot(self,
             context,
             output,
             bbox,
             crs,
             format,
             height,
             layers,
             styles,
             version,
             width,
             transparent,
             _macro=False,
             bgcolor=None,
             elevation=None,
             exceptions=None,
             time=None,
             ):
        try:
            crs = _CRSS[crs]
        except KeyError:
            raise ValueError("Unsupported CRS '{}'".format(crs))

        try:
            magics_format = MAGICS_OUTPUT_TYPES[format]
        except KeyError:
            raise errors.InvalidFormat(format)

        output_fname = output.target(magics_format)
        print("OUTPUT", output_fname)
        path, _ = os.path.splitext(output_fname)

        with LOCK:
            min_x, min_y, max_x, max_y = bbox
            # Magics is talking in cm.
            width_cm = width / 40.
            height_cm = height / 40.
            macro.silent()

            args = [
                macro.output(output_formats=[magics_format],
                             output_name_first_page_number='off',
                             output_cairo_transparent_background=transparent,
                             output_width=width,
                             output_name=path),
                macro.mmap(subpage_map_projection=crs.name,
                           subpage_lower_left_latitude=min_x,
                           subpage_lower_left_longitude=min_y,
                           subpage_upper_right_latitude=max_x,
                           subpage_upper_right_longitude=max_y,
                           subpage_frame='off',
                           page_x_length=width_cm,
                           page_y_length=height_cm,
                           super_page_x_length=width_cm,
                           super_page_y_length=height_cm,
                           subpage_x_length=width_cm,
                           subpage_y_length=height_cm,
                           subpage_x_position=0.,
                           subpage_y_position=0.,
                           output_width=width,
                           page_frame='off',
                           page_id_line='off',),
            ]

            for layer, style in zip(layers, styles):
                style = layer.style(style)
                args += layer.render(context, macro, style)

            if _macro:
                return self.macro_text(args,
                                       output.target('.py'),
                                       getattr(context, 'data_url', None),
                                       layers,
                                       styles)

            # self.log.debug('plot(): Calling macro.plot(%s)', args)
            try:
                macro.plot(*args)
            except Exception as e:
                self.log.exception('Magics error: %s', e)
                raise

            self.log.debug('plot(): Size of %s: %s',
                           output_fname, os.stat(output_fname).st_size)

            return output_fname


    def legend(self,
             context,
             output,
             format,
             height,
             layer,
             style,
             version,
             width,
             transparent
             ):



        try:
            magics_format = MAGICS_OUTPUT_TYPES[format]
        except KeyError:
            raise errors.InvalidFormat(format)

        output_fname = output.target(magics_format)
        print(output_fname)
        path, _ = os.path.splitext(output_fname)

        with LOCK:

            # Magics is talking in cm.
            width_cm = float(width )/ 40.
            height_cm = float(height)/ 40.

            args = [
                macro.output(output_formats=[magics_format],
                             output_name_first_page_number='off',
                             output_cairo_transparent_background=transparent,
                             output_width=width,
                             output_name=path),
                macro.mmap(
                           subpage_frame='off',
                           page_x_length=width_cm,
                           page_y_length=height_cm,
                           super_page_x_length=width_cm,
                           super_page_y_length=height_cm,
                           subpage_x_length=width_cm,
                           subpage_y_length=height_cm,
                           subpage_x_position=0.,
                           subpage_y_position=0.,
                           output_width=width,
                           page_frame='off',
                           page_id_line='off',),

            ]


            contour = layer.style(style, )

            args += layer.render(context, macro, contour, { 'legend' : 'on', "contour_legend_only" : True})

            legend_font_size = "25%"
            if width_cm < height_cm :
                legend_font_size = "5%"


            legend = macro.mlegend(
                  legend_title = "on",
                  legend_title_text = layer.title,
                  legend_display_type = "continuous",
                  legend_box_mode = "positional",
                  legend_only = True,
                  legend_box_x_position = 0.00,
                  legend_box_y_position = 0.00,
                  legend_box_x_length = width_cm,
                  legend_box_y_length = height_cm,
                  legend_box_blanking = not transparent,
                  legend_text_font_size = legend_font_size,
                  legend_text_colour = "navy",

            )

            # self.log.debug('plot(): Calling macro.plot(%s)', args)
            try:
                macro.plot(*args, legend)
            except Exception as e:
                self.log.exception('Magics error: %s', e)
                raise


            self.log.debug('plot(): Size of %s: %s',
                           output_fname, os.stat(output_fname).st_size)

            return output_fname

    def macro_text(self, args, output, data_url, layers, styles):
        head = []
        for layer, style in zip(layers, styles):
            style = layer.style(style)
            head.append('# LAYER: %s' % (layer,))
            head.append('# STYLE: %s' % (style,))

        path = None
        text = []
        for a in args:
            params = dict(**a.args)
            for k, v in list(params.items()):
                if k in ('output_name', 'netcdf_filename', 'grib_input_file_name'):
                    params[k] = os.path.basename(v)

                if 'netcdf_filename' in params:
                    path = params['netcdf_filename']

                if 'grib_input_file_name' in params:
                    path = params['grib_input_file_name']

            text.append('')

            text.append("a = %s" % (pprint.pformat(params),))
            text.append('args.append(macro.%s(**a))' % (a.verb,))

        if path and data_url:
            text.append('download("%s", "%s")' % (data_url, path))

        with open(output, 'w') as f:
            f.write(MACRO_TEXT.format('\n'.join(head), '\n'.join(text)))

        return output


class Styler(datatypes.Styler):

    log = logging.getLogger(__name__)

    def netcdf_styles(self, field, ncvar, path, variable):
        with LOCK:
            try:
                styles = macro.wmsstyles(macro.mnetcdf(netcdf_filename=path,
                                                       netcdf_value_variable=variable))
            # Looks like they are provided in reverse order

                return [MagicsWebStyle(**s) for s in styles.get('styles', [])]
            except Exception as e:
                self.log.exception('netcdf_styles: Error: %s', e)
                styles = {}

        return [MagicsWebStyle(**s) for s in styles.get('styles', [])]

    def grib_styles(self, field, grib, path, index):
        with LOCK:
            try:
                styles = macro.wmsstyles(macro.mgrib(grib_input_file_name=path,
                                                     grib_field_position=index + 1))
                # Looks like they are provided in reverse order
            except Exception as e:
                self.log.exception('grib_styles: Error: %s', e)
                styles = {}

        return [MagicsWebStyle(**s) for s in styles.get('styles', [])]

    def contours(self, field, driver, style, legend={}):
        if style is None:
            return driver.mcont()

        return driver.mcont(legend, contour_automatic_setting='style_name',
                            contour_style_name=style.name,
                            )
