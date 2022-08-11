# (C) Copyright 2012-2019 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation nor
# does it submit to any jurisdiction.

from pprint import pprint
from typing import Any, Dict, List
from skinnywms import datatypes
from dateutil import parser
import logging
import os
import datetime
import geojson

from skinnywms.server import WMSServer



class GeoJSONField(datatypes.Field):

    log = logging.getLogger(__name__)

    def __init__(self, context:WMSServer, path:str, featureCollection:geojson.FeatureCollection, name:str,time:str):

        self.path = path
        self.featureCollection = featureCollection
        self.time = parser.parse(time).astimezone(tz = datetime.timezone.utc) #datetime.datetime.now()
        self.levelist = None
        self.name = name
        self.title = self.name
        self.group_name = name
        self.group_title = self.group_name
        self.styles=[self.name]

    

    def render(self, context:WMSServer, driver, style, legend={}):
        data = []

        geojsonstring = geojson.dumps(self.featureCollection)
        #pprint(geojsonstring)

        if self.name == "mosmix" :
            data.append(driver.mgeojson(
            geojson_input_type = "string",
            geojson_input = geojsonstring
            )
        )
        else : 
            data.append(driver.mgeojson(
                geojson_input_type = "string",
                geojson_input = geojsonstring,
                geojson_value_property = self.name
                )
            )
        data.append(
            context.styler.symbol(self, driver, style, legend)
        )

        return data

    def as_dict(self):
        return dict(
            _class=self.__class__.__module__ + "." + self.__class__.__name__,
            name=self.name,
            title=self.title,
            path=self.path,
            index=self.index,
            mars=self.mars,
            styles=[s.as_dict() for s in self.styles],
            time=self.time.isoformat() if self.time is not None else None,
        )

    def __repr__(self):
        return "GeoJSONField[%r,%r,%r]" % (self.path, self.name, self.time)


class GeoJSONReader(datatypes.FieldReader):

    """Get WMS layers from a GeoJSON file."""

    log = logging.getLogger(__name__)

    SUPPORTED_TYPES = { "Feature", "FeatureCollection"}
    SUPPORTED_GEOMETRIES = { "Point" }
    REQUIRED_FIELDS = {"geometry", "type", "properties"}
    REQUIRED_PROPERTIES = {"time"}
    SUPPORTED_PROPERTIES = {
        "time",
        "name",
        "air_temperature",
        "wind_to_direction",
        "wind_speed",
        "precipitation_amount",
        "thunderstorm_probability",
        "surface_air_pressure_reduced",
        "cloud_area_fraction",
        "present_weather",
    }

    def __init__(self, context:WMSServer, path:str):
        super(GeoJSONReader,self).__init__(context=context, path=path)

    def build_features(point:geojson.Point, properties:Dict[str,Any], split_properties:bool=True, name:str="") -> List[geojson.Feature]:
        features:List[geojson.Feature] = []
        time:str = None
        if "time" not in properties.keys():
            GeoJSONReader.log.error("'time' field missing in timeseries property, skipping...")
        else:
            time = properties["time"]

        # if "name" in properties.keys():
        #     name = properties["name"]
        
        if split_properties:
            for item_name,item_value in properties.items():
                item_name = item_name.lower()
                if item_name == "time":
                    continue
                elif item_name in GeoJSONReader.SUPPORTED_PROPERTIES:
                    prop = { 
                        "time" : time,
                        "name" : name, # station name
                        item_name : item_value,
                    }
                    features.append(
                        geojson.Feature(geometry=point, properties=prop)
                    )
        else:
            # do not split properties, just include the known ones
            filtered_props = {}
            for item_name,item_value in properties.items():
                if item_name in GeoJSONReader.SUPPORTED_PROPERTIES:
                    filtered_props[item_name] = item_value
            
            filtered_props["name"] = name
            features.append(
                geojson.Feature(geometry=point, properties=filtered_props)
            )
        return features

    def extract_features(feature:Dict[str,Any], split_properties:bool=True) -> List[geojson.Feature]:
        features:List[geojson.Feature] = []
        props = set(feature.keys())
        diff = GeoJSONReader.REQUIRED_FIELDS.difference(props)
        if len(diff) > 0:
            GeoJSONReader.log.error("Missing Feature properties: ", diff)
            return
        if feature["type"] != "Feature":
            GeoJSONReader.log.error("Unsupported feature type", feature["type"])
            return
        
        point = geojson.Point(coordinates=feature["geometry"]["coordinates"])

        name = ""
        if "name" in feature["properties"].keys():
            name = feature["properties"]["name"]

        if "timeseries" in feature["properties"].keys():
            timeseries:List[Dict[str,Any]] = feature["properties"]["timeseries"]
            for ts_props in timeseries:
                features.extend(
                    GeoJSONReader.build_features(
                        point=point,
                        properties=ts_props, 
                        split_properties=split_properties,
                        name=name
                    )
                )
        else:
            # not a timeseries, but a value for a single time step
            features.extend(
                GeoJSONReader.build_features(
                    point=point, 
                    properties=feature["properties"], 
                    split_properties=split_properties,
                    name=name
                )
            )

        return features

    def get_fields(self) -> list:
        self.log.info("Scanning file:", self.path)

        features:List[geojson.Feature] = []
        features_grouped:List[geojson.Feature] = []
        with open(self.path) as file:
            content = geojson.load(file)
            content:Dict[str,Any]
            if "type" in content.keys():
                if content["type"] == "FeatureCollection":
                    self.log.info("FeatureCollection found!")
                    for ft in content["features"]:
                        features.extend(
                            GeoJSONReader.extract_features(feature=ft)
                        )
                        features_grouped.extend(
                            GeoJSONReader.extract_features(feature=ft, split_properties=False)
                        )
                elif content["type"] == "Feature":
                    self.log.info("Feature found!")
                    features.extend( 
                        GeoJSONReader.extract_features(feature=content)
                    )
                    features_grouped.extend(
                        GeoJSONReader.extract_features(feature=content, split_properties=False)
                    )
                else:
                    self.log.error("Unsupported type:", content["type"])
                    return []
            else:
                self.log.error("GeoJSON 'type' not found. Skipping file.")
                return []

        features_by_field:Dict[str,Dict[str,List[geojson.Feature]]] = {}
        skip_fields = {"time", "name"}
        for feature in features:
            field_name = set(feature["properties"].keys()).difference(skip_fields).pop()
            time = feature["properties"]["time"]

            # feature by field
            if field_name not in features_by_field.keys():
                features_by_field[field_name] = {}
            
            if time not in features_by_field[field_name].keys():
                features_by_field[field_name][time] = []

            features_by_field[field_name][time].append(feature)

        features_by_time:Dict[str,List[geojson.Feature]] = {}
        for feature in features_grouped:
            time = feature["properties"]["time"]

            # features by time
            if time not in features_by_time.keys():
                features_by_time[time] = []
            features_by_time[time].append(feature)

        #pprint(features_by_field)

        fields = []

        for field_name, field_value in features_by_field.items():
            for time, time_collection in field_value.items():
                feature_collection = geojson.FeatureCollection(features=time_collection)
                fields.append(GeoJSONField(self.context, self.path, featureCollection=feature_collection, name=field_name, time=time))

        # extract layer name from file name
        name = os.path.basename(self.path)
        layer_name, ext = os.path.splitext(name) 
        for time, time_collection in features_by_time.items():
            feature_collection = geojson.FeatureCollection(features=time_collection)
            fields.append(GeoJSONField(self.context, self.path, featureCollection=feature_collection, name=layer_name, time=time))
        return fields
