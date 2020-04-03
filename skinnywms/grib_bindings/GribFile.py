# (C) Copyright 2012-2019 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation nor
# does it submit to any jurisdiction.
#

import os
from .bindings import grib_file_open

from .GribField import GribField


class GribFile(object):
    def __init__(self, path):

        if path.startswith("~"):
            path = os.path.expanduser(path)

        self.path = path
        self.file = grib_file_open(path)

    def __del__(self):
        try:
            self.file.close()
        except Exception:
            pass

    def __iter__(self):
        return self

    def __next__(self):
        return self.next()

    def at_offset(self, offset):
        self.file.position(offset)
        return self.next()

    def next(self):
        here = self.file.tell()
        h = self.file.next()
        if not h:
            raise StopIteration()
        return GribField(h, self.path, here)
