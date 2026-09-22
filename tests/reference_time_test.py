# (C) Copyright 2012-2019 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation nor
# does it submit to any jurisdiction.

"""Tests for the optional forecast reference time ('forecast run') dimension.

These exercise datatypes.DataLayer/Availability directly with synthetic fields,
so that no grib file, magics installation or running server is needed.
"""

import datetime

import pytest

from skinnywms import protocol
from skinnywms.datatypes import Availability, DataLayer, TimeDimension

UTC = datetime.timezone.utc

RUN_00 = datetime.datetime(2019, 1, 1, 0, 0, tzinfo=UTC)
RUN_12 = datetime.datetime(2019, 1, 1, 12, 0, tzinfo=UTC)


class FakeField:
    """The smallest thing a DataLayer will accept as a field."""

    def __init__(self, name="2t", time=None, levelist=None, reference_time=None):
        self.name = name
        self.title = name.upper()
        self.group_name = name
        self.group_title = name.upper()
        self.time = time
        self.levelist = levelist
        self.levtype = "sfc" if levelist is None else "pl"
        self.reference_time = reference_time
        self.styles = []

    def __repr__(self):
        return "FakeField[%s,%s,%s]" % (self.name, self.reference_time, self.time)


def valid_time(run, step):
    return run + datetime.timedelta(hours=step)


def two_runs(steps=(0, 12), levelist=None):
    """Two forecast runs, 12 hours apart, with overlapping validity times."""
    fields = []
    for run in (RUN_00, RUN_12):
        for step in steps:
            fields.append(
                FakeField(
                    time=valid_time(run, step),
                    levelist=levelist,
                    reference_time=run,
                )
            )
    return fields


def layer(fields, **kwargs):
    data_layer = DataLayer(fields[0], **kwargs)
    for field in fields[1:]:
        data_layer.add_field(field)
    return data_layer


def dimension(data_layer, name):
    for dim in data_layer.dimensions:
        if dim.name == name:
            return dim
    return None


def test_equals_is_symmetric():
    # a signed comparison used to report every earlier time as equal
    assert TimeDimension.equals(RUN_00, RUN_00)
    assert not TimeDimension.equals(RUN_00, RUN_12)
    assert not TimeDimension.equals(RUN_12, RUN_00)
    assert TimeDimension.equals(None, None)
    assert not TimeDimension.equals(None, RUN_00)


def test_disabled_keeps_previous_behaviour():
    # without the option, runs still collide: 2 runs x 2 steps, sharing 12:00Z,
    # collapse onto the 3 distinct validity times
    data_layer = layer(two_runs())

    assert len(data_layer.available_reference_times()) == 0
    assert len(data_layer.available_times()) == 3
    assert dimension(data_layer, "reference_time") is None
    assert dimension(data_layer, "time") is not None


def test_disabled_ignores_a_requested_reference_time():
    data_layer = layer(two_runs())
    field = data_layer.select(
        {"reference_time": "2019-01-01T00:00:00Z", "time": None, "elevation": None}
    )

    assert field is data_layer._first


def test_enabled_keeps_both_runs():
    data_layer = layer(two_runs(), reference_time_dimension=True)

    assert data_layer.available_reference_times() == [RUN_00, RUN_12]
    # both runs are kept whole, including the shared 12:00Z validity time
    assert len(data_layer._fields) == 4
    assert data_layer.available_times(reference_time=RUN_00) == [RUN_00, RUN_12]
    assert data_layer.available_times(reference_time=RUN_12) == [
        RUN_12,
        valid_time(RUN_12, 12),
    ]


def test_enabled_advertises_the_dimension():
    dim = dimension(layer(two_runs(), reference_time_dimension=True), "reference_time")

    assert dim is not None
    assert dim.name == "reference_time"
    assert dim.units == "ISO8601"
    # the latest run is the most useful default
    assert dim.default == "2019-01-01T12:00:00Z"
    assert dim.extent == "2019-01-01T00:00:00Z,2019-01-01T12:00:00Z"


def test_evenly_spaced_runs_collapse_to_a_period():
    fields = [
        FakeField(time=run, reference_time=run)
        for run in (RUN_00, RUN_12, valid_time(RUN_00, 24))
    ]
    dim = dimension(layer(fields, reference_time_dimension=True), "reference_time")

    # the period notation is inherited from TimeDimension, including its quirk of
    # not folding the first timestamp into the range it starts
    assert dim.extent == (
        "2019-01-01T00:00:00Z,2019-01-01T12:00:00Z/2019-01-02T00:00:00Z/PT12H"
    )


def test_a_single_run_advertises_no_dimension():
    # nothing to select, and existing single-run datasets must keep the
    # capabilities they have always had
    data_layer = layer(
        [FakeField(time=RUN_00, reference_time=RUN_00)],
        reference_time_dimension=True,
    )

    assert dimension(data_layer, "reference_time") is None
    assert dimension(data_layer, "time") is not None


def test_select_picks_the_requested_run():
    data_layer = layer(two_runs(), reference_time_dimension=True)

    # 12:00Z is both the T+12 of the 00Z run and the T+0 of the 12Z run:
    # the same validity time has to resolve to two different fields
    from_00 = data_layer.select(
        {"reference_time": "2019-01-01T00:00:00Z", "time": "2019-01-01T12:00:00Z"}
    )
    from_12 = data_layer.select(
        {"reference_time": "2019-01-01T12:00:00Z", "time": "2019-01-01T12:00:00Z"}
    )

    assert from_00.reference_time == RUN_00
    assert from_12.reference_time == RUN_12
    assert from_00.time == from_12.time == RUN_12
    assert from_00 is not from_12


def test_select_defaults_to_the_latest_run():
    data_layer = layer(two_runs(), reference_time_dimension=True)
    field = data_layer.select({"time": "2019-01-02T00:00:00Z"})

    assert field.reference_time == RUN_12
    assert field.time == valid_time(RUN_12, 12)


def test_select_snaps_to_the_nearest_earlier_run():
    data_layer = layer(two_runs(), reference_time_dimension=True)

    # a run we do not hold: never answer with a more recent one than requested
    field = data_layer.select({"reference_time": "2019-01-01T06:00:00Z"})
    assert field.reference_time == RUN_00

    # a run older than anything we hold: fall back to the advertised default
    field = data_layer.select({"reference_time": "2018-01-01T00:00:00Z"})
    assert field.reference_time == RUN_12


def test_select_resolves_time_within_the_requested_run():
    # only the 12Z run reaches 2019-01-02T00:00Z, asking the 00Z run for it must
    # not silently return the other run's field
    data_layer = layer(two_runs(), reference_time_dimension=True)
    field = data_layer.select(
        {"reference_time": "2019-01-01T00:00:00Z", "time": "2019-01-02T00:00:00Z"}
    )

    assert field.reference_time == RUN_00
    assert field.time == valid_time(RUN_00, 12)


def test_select_combines_reference_time_and_elevation():
    data_layer = layer(
        two_runs(levelist=500) + two_runs(levelist=850),
        reference_time_dimension=True,
        group_dimensions=True,
    )

    assert data_layer.available_elevations() == ["500", "850"]
    field = data_layer.select(
        {
            "reference_time": "2019-01-01T00:00:00Z",
            "time": "2019-01-01T12:00:00Z",
            "elevation": "850",
        }
    )

    assert field.reference_time == RUN_00
    assert field.time == RUN_12
    assert field.levelist == 850


def test_select_raises_on_an_unknown_time():
    data_layer = layer(two_runs(), reference_time_dimension=True)

    with pytest.raises(KeyError):
        # earlier than any validity time of any run
        data_layer.select({"time": "2018-01-01T00:00:00Z"})


def test_availability_passes_the_option_to_its_layers():
    availability = Availability(reference_time_dimension=True)
    for field in two_runs():
        availability.add_field(field)

    assert availability.reference_time_dimension
    data_layer = availability._layers["2t"]
    assert data_layer.reference_time_dimension
    assert len(data_layer._fields) == 4

    field = availability.layer("2t", {"reference_time": "2019-01-01T00:00:00Z"})
    assert field.reference_time == RUN_00


def test_availability_defaults_to_the_option_being_off():
    availability = Availability()
    for field in two_runs():
        availability.add_field(field)

    assert not availability.reference_time_dimension
    assert not availability._layers["2t"].reference_time_dimension


@pytest.mark.parametrize("version", ["1.1.1", "1.3.0"])
def test_getmap_accepts_dim_reference_time(version):
    params = {
        "DIM_REFERENCE_TIME": "2019-01-01T00:00:00Z",
        "REQUEST": "GetMap",
        "SOMETHING_ELSE": "x",
    }
    wms, non_wms = protocol.filter_wms_params(params)

    # must survive the allow-list, or it never reaches get_map()
    assert wms["dim_reference_time"] == "2019-01-01T00:00:00Z"
    assert "dim_reference_time" not in non_wms

    known = [name for (name, _, _) in protocol._WMS_KNOWN_PARAMS[("getmap", version)]]
    assert "dim_reference_time" in known
