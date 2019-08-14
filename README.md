

The skinny WMS is a small WMS server that will help you to visualise your NetCDF and Grib Data

Features:
- 

Limitations:

- development stage: **Alpha**,


Installation
------------

SkinnyWMS  depends on the ECMWF *Magics* library.

If you do not have *Magics* installed on your platform, skinnywms is available on conda forge https://conda-forge.org/::

    $ conda config --add channels conda-forge
    $ conda install skinnywms
    

If you have *Magics* already installed you can use pip::

    $ pip install skinnywms
    
Usage
-----




How to install Magics
-----------------------

that must be installed on the system and accessible as a shared library.
Some Linux distributions ship a binary version that may be installed with the standard package manager.


As an alternative you may install the official source distribution
by following the instructions at
https://software.ecmwf.int/magics/Installation+Guide

Note that *Magics* support for the Windows operating system is experimental.




Contributing
------------

The main repository is hosted on GitHub,
testing, bug reports and contributions are highly welcomed and appreciated:

https://github.com/ecmwf/skinnywms

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

