

The skinny WMS is a small WMS server that will help you to visulaise your NetCDF and Grib Data

Features:
- 

Limitations:

- development stage: **Alpha**,


Installation
------------

The package is installed from PyPI with::

    $ pip install skinny-wms


System dependencies
~~~~~~~~~~~~~~~~~~~

The python module depends on the ECMWF *Magics* library
that must be installed on the system and accessible as a shared library.
Some Linux distributions ship a binary version that may be installed with the standard package manager.
On Ubuntu 18.04 use the command::

    $ sudo apt-get install libmagplus

As an alternative you may install the official source distribution
by following the instructions at
https://software.ecmwf.int/magics/Installation+Guide

Note that *Magics* support for the Windows operating system is experimental.

You may run a simple selfcheck command to ensure that your system is set up correctly::

    $ python -m Magics selfcheck
    Found: Magics '4.1.2'.
    Your system is ready.


Usage
-----


Contributing
------------

The main repository is hosted on GitHub,
testing, bug reports and contributions are highly welcomed and appreciated:

https://github.com/sylvielamythepaut/skinny-wms

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

