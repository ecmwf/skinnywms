
The skinny WMS is a small WMS server that will help you to visualise your NetCDF and Grib Data.
The principle is simple: skinny will browse the directory, or the single file passed as argument, and try to interpret each NetCDF or GRIB files. From the metadata, it will be built the getCapabilities document, and find a relevant style to plot the data.

[![build](https://img.shields.io/travis/ecmwf/skinnywms/master.svg)](https://travis-ci.org/ecmwf/skinnywms/branches)
[![Docker Build Status](https://img.shields.io/docker/cloud/build/ecmwf/skinnywms.svg)](https://hub.docker.com/r/ecmwf/skinnywms)
[![Docker Pulls](https://img.shields.io/docker/pulls/ecmwf/skinnywms)](https://hub.docker.com/r/ecmwf/skinnywms)[![PyPI version](https://badge.fury.io/py/skinnywms.svg)](https://badge.fury.io/py/skinnywms) [![Anaconda-Server Badge](https://anaconda.org/conda-forge/skinnywms/badges/version.svg)](https://anaconda.org/conda-forge/skinnywms) [![Anaconda-Server Badge](https://anaconda.org/conda-forge/skinnywms/badges/downloads.svg)](https://anaconda.org/conda-forge/skinnywms)


Features:
---------
SkinnyWMS implements 3 of the WMS endpoints:
- **getCapabilities**: Discover the data, build an XML Document presenting each identified parameter in the file(s) as a layer with the list of their predefined styles. (There is always a default style)
- **getMap** : Return the  selected layer suing the selected style.
- **getLegendGraphic**: Return the legend.


Usage:
-----
There are 2 ways to start using it, they both will start a small Flask server.
Once running, a small leaflet client is accessible [http://127.0.0.1:5000/]

* The demo:

```bash
python demo.py --path /path/to/mydata
```

* The command line:

```bash
skinny-wms --path /path/to/mydata
```

* Or with uwsgi:

```bash
uwsgi --http localhost:5000 --master --process 20 --mount /=skinnywms.wmssvr:application --env SKINNYWMS_DATA_PATH=/path/to/mydata
```


Run using Docker
----------------

By default the docker image will start the application using uwsgi and will load and display some demo data.

* Run the demo:
```bash
docker run --rm -p 5000:5000 -it ecmwf/skinnywms 
```
Now you can try the leaflet demo at http://localhost:5000/

* Run using data on your machine:
```bash
docker run --rm -p 5000:5000 -it \
    --volume=/path/to/my/data:/path/inside/the/container \
    --env SKINNYWMS_DATA_PATH=/path/inside/the/container \
      ecmwf/skinnywms
```
Now you can access the leaflet demo with your data at http://localhost:5000/

* Configure different options by setting environment variables accordingly:
```bash
docker run --rm -p 5000:5000 -it \
    --volume=/path/to/my/data:/path/inside/the/container \
    --env SKINNYWMS_DATA_PATH=/path/inside/the/container \
    --env SKINNYWMS_HOST=0.0.0.0 \
    --env SKINNYWMS_PORT=5000 \
    --env SKINNYWMS_MOUNT=/mymodel/ \
    --env SKINNYWMS_UWSGI_WORKERS=4 \
    --env SKINNYWMS_ENABLE_DIMENSION_GROUPING=1 \
      ecmwf/skinnywms
```
Now you can access the ```GetCapabilities`` document for your data at http://localhost:5000/mymodel/wms?request=GetCapabilities


Installation
------------

SkinnyWMS  depends on the ECMWF *Magics* library.

If you do not have *Magics* installed on your platform, skinnywms is available on conda forge https://conda-forge.org/

```bash
conda config --add channels conda-forge
conda install skinnywms
```

If you have *Magics* already installed you can use pip:

```bash
pip install skinnywms
```

Limitations:
------------
- SkinnyWMS will perform better on well formatted and documented NetCDF and GRIB.

- grib fields containing corresponding wind components u,v need to be placed together in a single grib file in order to be displayed as vectors/wind barbs in SkinnyWMS. You can combine multiple grib files into a single file using ecCodes ``grib_copy`` (included in the docker image), e.g.:
```bash
grib_copy input_wind_u_component.grb2 input_wind_v_component.grib2 output_wind_u_v_combined.grb2
```

- The time and elevation dimension implementations follow [OGC Met Ocean DWG WMS 1.3 Best Practice for using Web Map Services (WMS) with Time-Dependent or Elevation-Dependent Data](https://external.ogc.org/twiki_public/MetOceanDWG/MetOceanWMSBPOnGoingDrafts). To enable dimension grouping (disabled by default) set the environment variable ``SKINNYWMS_ENABLE_DIMENSION_GROUPING=1``

- development stage: **Alpha**,


Add your own styles:
--------------------

Multi-process
-------------

Cache
-----


How to install Magics
-----------------------

that must be installed on the system and accessible as a shared library.
Some Linux distributions ship a binary version that may be installed with the standard package manager.


As an alternative you may install the official source distribution
by following the instructions at
https://software.ecmwf.int/magics/Installation+Guide
Magics is available on github https://github.com/ecmwf/magics

Note that *Magics* support for the Windows operating system is experimental.


Start up a local development environment (Docker)
-----------------------------------------

Make sure you have ``Docker`` and ``docker-compose`` installed. Then run:
```bash
docker-compose up
```
This will build a dev image and start up a local flask development server (with automatic reload on code changes) at http://localhost:5000 based on the configuration stored in [docker-compose.yml](./docker-compose.yml) and [.env](./.env) and by default try to load all GRIB and NetCDF data stored in [skinnywms/testdata](./skinnywms/testdata).


Contributing
------------

The main repository is hosted on GitHub,
testing, bug reports and contributions are highly welcomed and appreciated:

https://github.com/ecmwf/skinnywms
https://github.com/ecmwf/magics-python
https://github.com/ecmwf/magics


Please see the CONTRIBUTING.rst document for the best way to help.

Lead developers:

- `Sylvie Lamy-Thepaut <https://github.com/sylvielamythepaut>`_ - ECMWF
- `Baudouin Raoult <https://github.com/b8raoult>` - ECMWF
- `Eduard Rosert <https://github.com/eduardRosert>` - ECMWF

Main contributors:

- `Stephan Siemen <https://github.com/stephansiemen>`_ - ECMWF
- `Milana Vuckovic <https://github.com/milanavuckovic>` - ECMWF


License
-------

Copyright 2017-2019 European Centre for Medium-Range Weather Forecasts (ECMWF).

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at: http://www.apache.org/licenses/LICENSE-2.0.
Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

