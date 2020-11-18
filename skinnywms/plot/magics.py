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
import json

from Magics import macro

from skinnywms import datatypes, errors


__all__ = [
    "Plotter",
]


mimetypes.add_type("application/x-grib", ".grib", strict=False)
mimetypes.add_type("application/x-netcdf", ".nc", strict=False)
mimetypes.add_type("application/x-netcdf", ".nc4", strict=False)


_CRSS = {crs["name"]: datatypes.CRS(**crs) for crs in macro.wmscrs()["crss"]}


MAGICS_OUTPUT_TYPES = {
    "image/png": "png",
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
        return [
            driver.mcoast(
                map_coastline_general_style=self.name, map_coastline_resolution="medium"
            )
        ]

    def __repr__(self):
        return "StaticLayer[%s]" % (self.name,)


class OceanLayer(StaticLayer):
    def render(self, context, driver, style):
        return [
            driver.mcoast(
                map_coastline_sea_shade_colour="#f2f2f2",
                map_grid="off",
                map_coastline_sea_shade="on",
                map_label="off",
                map_coastline_colour="#f2f2f2",
                map_coastline_resolution="medium",
            )
        ]

    def __repr__(self):
        return "OceanLayer[%s]" % (self.name,)


class USLayer(StaticLayer):
    def render(self, context, driver, style):
        return [
            driver.mcoast(
                map_grid="off",
                map_boundaries="on",
                map_administrative_boundaries="on",
                map_administrative_boundaries_countries_list=["USA"],
                map_label="off",
                map_coastline_colour="none",
                map_administrative_boundaries_colour="tan",
                map_coastline_resolution="medium",
            )
        ]

    def __repr__(self):
        return "USLayer[%s]" % (self.name,)


class UserBaseLayer(StaticLayer):
    def render(self, context, driver, style):
        return [
            driver.mcoast(
                map_user_layer="on",
                map_user_layer_name=self.layer,
                map_user_layer_colour="charcoal",
                map_user_layer_thickness=1,
                map_grid=False,
                map_coastline_colour="none",
            )
        ]

    def __repr__(self):
        return "UserBaseLayer[%s]" % (self.name,)


class MagicsWebStyle(datatypes.Style):
    pass


class Plotter(datatypes.Plotter):

    supported_crss = tuple(_CRSS.values())

    geographic_bounding_box = macro.wmscrs()["geographic_bounding_box"]

    log = logging.getLogger(__name__)

    def __init__(self, baselayer=None, styles=None):
        if styles is None:
            styles = {}
        self._styles = styles
        layers = [
            StaticLayer("foreground", title="Foreground", zindex=99999),
            StaticLayer("background", title="Background", zindex=-99999),
            StaticLayer("grid", title="Grid", zindex=99999),
            StaticLayer("boundaries", title="Boundaries", zindex=99999),
            OceanLayer("oceans", title="Oceans", zindex=99999),
            USLayer("us-states", title="Us States", zindex=99999),
        ]

        if baselayer:
            name = os.path.basename(baselayer)
            try:
                name = os.path.basename(baselayer)
            except:
                name = "user defined baselayer"
            base = UserBaseLayer(name, title=name, zindex=99999)
            base.layer = baselayer
            layers.append(base)

        self._layers = {layer.name: layer for layer in layers}

    def layers(self):
        for layer in self._layers.values():
            yield layer

    def layer(self, name, time=None):
        try:
            return self._layers[name]
        except KeyError:
            raise errors.LayerNotDefined("Unknown layer '{}'".format(name))

    def plot(
        self,
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

        lon_vertical = 0.0
        if crs.startswith("EPSG:32661:"):
            crs_name = "polar_north"
            lon_vertical = float(crs.split(":")[2])
        elif crs.startswith("EPSG:32761:"):
            crs_name = "polar_south"
            lon_vertical = float(crs.split(":")[2])
        elif crs == "EPSG:32761":
            crs_name = "EPSG:32761"
        else:
            try:
                crs = _CRSS[crs]
                crs_name = crs.name
            except KeyError:
                raise ValueError("Unsupported CRS '{}'".format(crs))

        try:
            magics_format = MAGICS_OUTPUT_TYPES[format]
        except KeyError:
            raise errors.InvalidFormat(format)

        output_fname = output.target(magics_format)
        path, _ = os.path.splitext(output_fname)

        with LOCK:
            min_x, min_y, max_x, max_y = bbox
            # Magics is talking in cm.
            width_cm = width / 40.0
            height_cm = height / 40.0
            macro.silent()

            coordinates_system = {"EPSG:4326": "latlon"}

            map_params = {
                "subpage_map_projection": crs_name,
                "subpage_lower_left_latitude": min_y,
                "subpage_lower_left_longitude": min_x,
                "subpage_upper_right_latitude": max_y,
                "subpage_upper_right_longitude": max_x,
                "subpage_coordinates_system": coordinates_system.get(
                    crs_name, "projection"
                ),
                "subpage_frame": "off",
                "page_x_length": width_cm,
                "page_y_length": height_cm,
                "super_page_x_length": width_cm,
                "super_page_y_length": height_cm,
                "subpage_x_length": width_cm,
                "subpage_y_length": height_cm,
                "subpage_x_position": 0.0,
                "subpage_y_position": 0.0,
                "output_width": width,
                "page_frame": "off",
                "skinny_mode": "on",
                "page_id_line": "off",
            }

            # add extra settings for polar stereographic projection when
            # vertical longitude is not 0
            if crs_name in ["polar_north", "polar_south"]:
                map_params["subpage_map_vertical_longitude"] = lon_vertical

            if crs_name in ["polar_north"]:
                map_params["subpage_map_true_scale_north"] = 90

            if crs_name in ["polar_south"]:
                map_params["subpage_map_true_scale_south"] = -90

            args = [
                macro.output(
                    output_formats=[magics_format],
                    output_name_first_page_number="off",
                    output_cairo_transparent_background=transparent,
                    output_width=width,
                    output_name=path,
                ),
                macro.mmap(**map_params),
            ]

            for layer, style in zip(layers, styles):
                style = layer.style(style)
                args += layer.render(context, macro, style)

            if _macro:
                return (
                    "text/x-python",
                    self.macro_text(
                        args,
                        output.target(".py"),
                        getattr(context, "data_url", None),
                        layers,
                        styles,
                    ),
                )

            # self.log.debug('plot(): Calling macro.plot(%s)', args)
            try:
                macro.plot(*args)
            except Exception as e:
                self.log.exception("Magics error: %s", e)
                raise

            self.log.debug(
                "plot(): Size of %s: %s", output_fname, os.stat(output_fname).st_size
            )

            return format, output_fname

    def legend(
        self, context, output, format, height, layer, style, version, width, transparent
    ):

        try:
            magics_format = MAGICS_OUTPUT_TYPES[format]
        except KeyError:
            raise errors.InvalidFormat(format)

        output_fname = output.target(magics_format)
        path, _ = os.path.splitext(output_fname)

        with LOCK:

            # Magics is talking in cm.
            width_cm = float(width) / 40.0
            height_cm = float(height) / 40.0

            args = [
                macro.output(
                    output_formats=[magics_format],
                    output_name_first_page_number="off",
                    output_cairo_transparent_background=transparent,
                    output_width=width,
                    output_name=path,
                ),
                macro.mmap(
                    subpage_frame="off",
                    page_x_length=width_cm,
                    page_y_length=height_cm,
                    super_page_x_length=width_cm,
                    super_page_y_length=height_cm,
                    subpage_x_length=width_cm,
                    subpage_y_length=height_cm,
                    subpage_x_position=0.0,
                    subpage_y_position=0.0,
                    output_width=width,
                    page_frame="off",
                    page_id_line="off",
                ),
            ]

            contour = layer.style(style,)

            args += layer.render(
                context, macro, contour, {"legend": "on", "contour_legend_only": True}
            )

            legend_font_size = "25%"
            if width_cm < height_cm:
                legend_font_size = "5%"

            legend_title = layer.title
            if hasattr(layer, legend_title):
                legend_title = layer.legend_title

            legend = macro.mlegend(
                legend_title="on",
                legend_title_text=legend_title,
                legend_display_type="continuous",
                legend_box_mode="positional",
                legend_only=True,
                legend_box_x_position=0.00,
                legend_box_y_position=0.00,
                legend_box_x_length=width_cm,
                legend_box_y_length=height_cm,
                legend_box_blanking=not transparent,
                legend_text_font_size=legend_font_size,
                legend_text_colour="white",
            )

            # self.log.debug('plot(): Calling macro.plot(%s)', args)
            try:
                macro.plot(*args, legend)
            except Exception as e:
                self.log.exception("Magics error: %s", e)
                raise

            self.log.debug(
                "plot(): Size of %s: %s", output_fname, os.stat(output_fname).st_size
            )

            return output_fname

    def macro_text(self, args, output, data_url, layers, styles):
        head = []
        for layer, style in zip(layers, styles):
            style = layer.style(style)
            head.append("# LAYER: %s" % (layer,))
            head.append("# STYLE: %s" % (style,))

        path = None
        text = []
        for a in args:
            params = dict(**a.args)
            for k, v in list(params.items()):
                if k in ("output_name", "netcdf_filename", "grib_input_file_name"):
                    params[k] = os.path.basename(v)

                if "netcdf_filename" in params:
                    path = params["netcdf_filename"]

                if "grib_input_file_name" in params:
                    path = params["grib_input_file_name"]

            text.append("")

            text.append("a = %s" % (pprint.pformat(params),))
            text.append("args.append(macro.%s(**a))" % (a.verb,))

        if path and data_url:
            text.append('download("%s", "%s")' % (data_url, path))

        with open(output, "w") as f:
            f.write(MACRO_TEXT.format("\n".join(head), "\n".join(text)))

        return output


class Styler(datatypes.Styler):

    log = logging.getLogger(__name__)

    def __init__(self,  user_style=None):
        self.user_style = None
        if user_style:
            try: 
                with open(user_style, "r") as f:
                    self.user_style = json.load(f)
                    if "name" not in self.user_style:
                        self.user_style["name"] = "user_style"
            except:
                self.user_style = None

    def netcdf_styles(self, field, ncvar, path, variable):
        if self.user_style:
            return [MagicsWebStyle(self.user_style["name"])]
        with LOCK:
            try:
                styles = macro.wmsstyles(
                    macro.mnetcdf(netcdf_filename=path, netcdf_value_variable=variable)
                )
                # Looks like they are provided in reverse order

                return [MagicsWebStyle(**s) for s in styles.get("styles", [])]
            except Exception as e:
                self.log.exception("netcdf_styles: Error: %s", e)
                styles = {}

        return [MagicsWebStyle(**s) for s in styles.get("styles", [])]

    def grib_styles(self, field, grib, path, index):
        if self.user_style:
            return [MagicsWebStyle(self.user_style["name"])]

        with LOCK:
            try:
                styles = macro.wmsstyles(
                    macro.mgrib(
                        grib_input_file_name=path, grib_field_position=index + 1
                    )
                )
                # Looks like they are provided in reverse order
            except Exception as e:
                self.log.exception("grib_styles: Error: %s", e)
                styles = {}

        return [MagicsWebStyle(**s) for s in styles.get("styles", [])]

    def contours(self, field, driver, style, legend={}):

        if self.user_style:
            return driver.mcont(self.user_style)

        if style is None:
            return driver.mcont()

        return driver.mcont(
            legend,
            contour_automatic_setting="style_name",
            contour_style_name=style.name,
        )
