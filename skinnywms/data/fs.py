# Copyright (C) ECMWF 2018

import logging
import os
import traceback
import threading

from skinnywms import datatypes
from skinnywms.fields.NetCDFField import NetCDFReader

from skinnywms.fields.GRIBField import GRIBReader

__all__ = [
    "Availability",
]

LOCK = threading.Lock()


class Availability(datatypes.Availability):

    log = logging.getLogger(__name__)

    def __init__(self, path, *args, **kwargs):
        super(Availability, self).__init__(*args, **kwargs)
        self._path = path
        self._paths = {}
        self._loaded = False

    def load(self):

        with LOCK:

            if self._loaded:
                return

            if os.path.isdir(self._path):

                for fname in sorted(os.listdir(self._path)):
                    fname = os.path.join(self._path, fname)
                    if not os.path.isfile(fname):
                        continue

                    self.add_file(fname)

            elif os.path.isfile(self._path):
                self.add_file(self._path)
            else:
                raise NotImplementedError(
                    "%s is neither a file not  a directory" % (self._path,)
                )

            self._loaded = True

    def add_file(self, path):
        self.log.info("Scanning %s", path)
        try:
            reader = _reader(self.context, path)
        except ValueError as exc:
            self.log.info("Skipping file %s: %s", path, exc)
            self._paths[path] = [traceback.format_exc()]
            return

        n = 0
        for field in reader.get_fields():
            n += 1
            self.add_field(field)

        self._paths[path] = n

    def as_dict(self):
        d = super(Availability, self).as_dict()
        d.update(dict(paths=self._paths))
        return d


READERS = {
    b"GRIB": GRIBReader,
    b"\x89HDF": NetCDFReader,
    b"CDF\x01": NetCDFReader,
    b"CDF\x02": NetCDFReader,
}


def _reader(context, path):
    with open(path, "rb") as f:
        header = f.read(4)

    if header in READERS:
        return READERS[header](context, path)

    raise ValueError("Unsupported file {} (header={})".format(path, header))
