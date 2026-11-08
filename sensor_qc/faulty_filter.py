"""
Three-pass filter that removes characteristic sensor malfunction patterns
from time-series data before analysis or storage.

Sensors fail in predictable ways:
  1. Readings exceed the physical range of the measurement (a sensor
     stuck at its max reports 500% oxygen saturation).
  2. The sensor gets stuck and returns the same value for hours — the
     flat-line pattern — often the last valid reading before failure.
  3. The probe is briefly removed from the medium, producing a transient
     near-zero spike immediately surrounded by normal readings.

Each pass targets one pattern and composes cleanly with the others.
"""
from __future__ import annotations
from typing import Optional

SENSOR_BOUNDS: dict[str, tuple[float, float]] = {
    "pH":                (2.0,  12.0),
    "orp":               (-800, 800),
    "temperature":       (0.0,  55.0),
    "conductivity":      (0.0,  150.0),
    "dissolved_oxygen":  (0.0,  45.0),
    "oxygen_saturation": (0.0,  300.0),
    "salinity":          (0.0,  100.0),
}

# Sensors that cannot legitimately read near-zero in a live bioreactor.
DIP_FILTER_SENSORS: frozenset[str] = frozenset(
    {"dissolved_oxygen", "oxygen_saturation", "conductivity", "temperature"}
)


def filter_faulty(
    timestamps: list,
    values: list[Optional[float]],
    sensor_key: str,
    min_flatline_run: int = 8,
) -> tuple[list, list[Optional[float]]]:
    """Remove faulty readings from a single sensor time series.

    Args:
        timestamps:        Parallel list of timestamps (any comparable type).
        values:            Parallel list of floats; None marks already-missing
                           points.
        sensor_key:        Key into SENSOR_BOUNDS and DIP_FILTER_SENSORS.
        min_flatline_run:  Consecutive near-identical readings that constitute
                           a stuck sensor. Default 8 = 2 hours at 15-minute
                           sampling interval.

    Returns:
        (timestamps, values) with faulty points removed.
    """
    if not values:
        return timestamps, values

    bounds = SENSOR_BOUNDS.get(sensor_key)

    # Pass 1: physical bounds
    pts: list = []
    pvs: list[float] = []
    for t, v in zip(timestamps, values):
        if v is None:
            continue
        if bounds and not (bounds[0] <= v <= bounds[1]):
            continue
        pts.append(t)
        pvs.append(v)

    if len(pvs) < 2:
        return pts, pvs

    # Pass 2: flat-line run detection (stuck sensor)
    # Consecutive readings varying less than 0.1% cannot come from a live
    # analogue signal — ADC noise alone would exceed that threshold.
    nulled = bytearray(len(pvs))
    run_start = 0
    for i in range(1, len(pvs) + 1):
        base = pvs[run_start]
        end_of_run = (
            i == len(pvs)
            or abs(pvs[i] - base) > max(abs(base) * 0.001, 0.001)
        )
        if end_of_run:
            if i - run_start >= min_flatline_run:
                for j in range(run_start, i):
                    nulled[j] = 1
            run_start = i

    # Pass 3: dip removal (probe-out-of-medium artefacts)
    if sensor_key in DIP_FILTER_SENSORS:
        active = [v for v, n in zip(pvs, nulled) if not n]
        if len(active) >= 4:
            p90 = sorted(active)[int(len(active) * 0.9)]
            min_valid = p90 * 0.05
            for i, v in enumerate(pvs):
                if not nulled[i] and v < min_valid:
                    nulled[i] = 1

    rts = [t for t, n in zip(pts, nulled) if not n]
    rvs = [v for v, n in zip(pvs, nulled) if not n]
    return rts, rvs
