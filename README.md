
The skinny WMS is a small WMS server that will help you to visualise your NetCDF and Grib Data.
The principle is simple: skinny will browse the directory, or the single file passed as argument, and try to inpterpret each NetCDF or GRIB files. From the metadata, it will be built the getCapabilities document, and find a relevant style to plot the data. 

[![build](https://img.shields.io/travis/ecmwf/skinnywms/master.svg)](https://travis-ci.org/ecmwf/skinnywms/branches)


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
$ python demo.py --path /path/to/mydata 
* The command line:
$ skinny-wms --path /path/to/mydata

Installation
------------

SkinnyWMS  depends on the ECMWF *Magics* library.

If you do not have *Magics* installed on your platform, skinnywms is available on conda forge https://conda-forge.org/::

    $ conda config --add channels conda-forge
    $ conda install skinnywms
    

If you have *Magics* already installed you can use pip::

    $ pip install skinnywms
    
Limitations:
------------
- SkinnyWMS will perform better on well formatted and documented NetCDF and GRIB.

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




Contributing
------------

The main repository is hosted on GitHub,
testing, bug reports and contributions are highly welcomed and appreciated:

https://github.com/ecmwf/skinnywms
https://github.com/ecmwf/magics-python
https://github.com/ecmwf/magics


Please see the CONTRIBUTING.rst document for the best way to help.

Lead developer:

- `Sylvie Lamy-Thepaut <https://github.com/sylvielamythepaut>`_ - ECMWF

Main contributors:

- `Baudouin Raoult` - ECMWF
- `Stephan Siemen <https://github.com/stephansiemen>`_ - ECMWF
- `Milana Vuckovic`- ECMWF


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

