import pytest
from sensor_qc.faulty_filter import filter_faulty

TS = [f"2024-01-01T{h:02d}:{m:02d}" for h in range(24) for m in (0, 15, 30, 45)]

def test_removes_above_physical_bounds():
    vals = [95.0, 98.0, 500.0, 94.0]   # 500% O2Sat is impossible
    _, rvs = filter_faulty(TS[:4], vals, "oxygen_saturation")
    assert 500.0 not in rvs

def test_removes_below_physical_bounds():
    vals = [7.5, 1.0, 7.6]             # pH 1.0 < minimum of 2.0
    _, rvs = filter_faulty(TS[:3], vals, "pH")
    assert 1.0 not in rvs

def test_detects_flatline_run():
    # 10 consecutive identical readings (> min_flatline_run=8) → removed
    vals = [9.1] * 10 + [9.0, 9.2, 9.1]
    _, rvs = filter_faulty(TS[:len(vals)], vals, "dissolved_oxygen")
    assert len(rvs) == 3

def test_short_run_not_removed():
    vals = [9.1] * 5 + [9.0, 9.2]     # 5 identical < threshold of 8
    _, rvs = filter_faulty(TS[:len(vals)], vals, "dissolved_oxygen")
    assert len(rvs) == 7

def test_dip_removal_for_o2sat():
    normal = [100.0, 105.0, 98.0, 102.0, 99.0, 101.0, 103.0, 100.0]
    vals = normal[:4] + [0.1] + normal[4:]
    _, rvs = filter_faulty(TS[:len(vals)], vals, "oxygen_saturation")
    assert 0.1 not in rvs

def test_no_dip_filter_for_pH():
    # pH near-zero is legitimate in acidic conditions; never remove
    vals = [2.5, 2.1, 2.3]
    _, rvs = filter_faulty(TS[:3], vals, "pH")
    assert len(rvs) == 3

def test_handles_none_input():
    vals = [9.0, None, 9.1]
    rts, rvs = filter_faulty(TS[:3], vals, "dissolved_oxygen")
    assert None not in rvs
    assert len(rts) == len(rvs)
