"""
Dynamically assigns sensor columns from tabular data files, skipping
text-only flag columns that some instruments insert mid-schema.

Background
----------
Some data loggers insert a boolean flag column (e.g. an "IsValid" or
"QC_Pass" Yes/No column) between two numeric sensor channels. A
fixed-index column map silently assigns the wrong physical quantity to
each downstream slot — Dissolved Oxygen ends up reading Conductivity
values, for example. The values look plausible; the sensor is wrong.
This module detects the insertion dynamically so the map stays correct
regardless of which file version it encounters.
"""
from __future__ import annotations
import pandas as pd

KNOWN_FLAGS = {"yes", "no", "true", "false", "pass", "fail"}


def _is_flag_column(col_vals: pd.Series) -> bool:
    if col_vals.empty:
        return False
    normalized = col_vals.astype(str).str.strip().str.lower()
    return normalized.isin(KNOWN_FLAGS).all()


def detect_sensor_columns(
    df: pd.DataFrame,
    fixed_cols: dict[int, str],
    remaining_sensors: list[str],
) -> dict[int, str]:
    """Return a complete {column_index: sensor_name} mapping.

    Fixed columns (timestamp, pH, ORP, temperature, conductivity) are
    taken as-is from fixed_cols. Starting from the column immediately
    after the last fixed column, this function scans forward, skips any
    column whose non-null values consist entirely of known flag values
    (yes/no/true/false/pass/fail), and assigns the remaining numeric
    columns to remaining_sensors in order.

    Args:
        df:                Raw DataFrame read with header=None so columns
                           are integer indices.
        fixed_cols:        {col_index: sensor_name} for the left-hand
                           columns that are always at known positions.
        remaining_sensors: Ordered sensor names to assign to the numeric
                           columns found after the fixed boundary.

    Returns:
        Complete mapping, including fixed_cols and newly detected columns.

    Raises:
        ValueError: If fewer numeric columns are found than remaining_sensors.
    """
    col_map = dict(fixed_cols)
    boundary = max(fixed_cols) + 1
    n_cols = df.shape[1]

    numeric_cols: list[int] = []
    for ci in range(boundary, n_cols):
        col_vals = df[ci].dropna()
        if not _is_flag_column(col_vals):
            numeric_cols.append(ci)
        if len(numeric_cols) >= len(remaining_sensors):
            break

    if len(numeric_cols) < len(remaining_sensors):
        raise ValueError(
            f"Expected {len(remaining_sensors)} sensor columns after the fixed "
            f"boundary but found only {len(numeric_cols)}. Check the source file."
        )

    for i, sensor_name in enumerate(remaining_sensors):
        col_map[numeric_cols[i]] = sensor_name

    return col_map


def apply_column_map(df: pd.DataFrame, col_map: dict[int, str]) -> pd.DataFrame:
    """Rename and select columns according to col_map, dropping the rest."""
    df = df.rename(columns=col_map)
    keep = list(dict.fromkeys(col_map.values()))
    return df[[c for c in keep if c in df.columns]].copy()
