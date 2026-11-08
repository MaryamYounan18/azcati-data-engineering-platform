import pandas as pd
import pytest
from sensor_qc.column_detector import detect_sensor_columns, apply_column_map

FIXED     = {0: "timestamp", 1: "pH", 2: "ORP", 3: "temperature", 4: "conductivity"}
REMAINING = ["dissolved_oxygen", "oxygen_saturation", "salinity"]

def make_df(rows):
    return pd.DataFrame(rows)

def test_no_flag_column():
    df = make_df([
        ["2024-01-01 08:00", 7.5, 230, 25.0, 15.2, 8.3, 95.0, 0.5],
        ["2024-01-01 08:15", 7.6, 225, 25.1, 15.3, 8.4, 96.0, 0.5],
    ])
    col_map = detect_sensor_columns(df, FIXED, REMAINING)
    assert col_map[5] == "dissolved_oxygen"
    assert col_map[6] == "oxygen_saturation"
    assert col_map[7] == "salinity"

def test_skips_yes_no_flag_column():
    df = make_df([
        ["2024-01-01 08:00", 7.5, 230, 25.0, 15.2, "Yes", 8.3, 95.0, 0.5],
        ["2024-01-01 08:15", 7.6, 225, 25.1, 15.3, "No",  8.4, 96.0, 0.5],
    ])
    col_map = detect_sensor_columns(df, FIXED, REMAINING)
    assert 5 not in col_map           # flag column must be skipped
    assert col_map[6] == "dissolved_oxygen"
    assert col_map[7] == "oxygen_saturation"
    assert col_map[8] == "salinity"

def test_all_null_column_not_skipped():
    df = make_df([
        ["2024-01-01 08:00", 7.5, 230, 25.0, 15.2, None, 8.3, 95.0, 0.5],
        ["2024-01-01 08:15", 7.6, 225, 25.1, 15.3, None, 8.4, 96.0, 0.5],
    ])
    col_map = detect_sensor_columns(df, FIXED, REMAINING)
    assert col_map[5] == "dissolved_oxygen"   # all-null is not text-only

def test_apply_drops_flag_column():
    df = make_df([
        ["2024-01-01 08:00", 7.5, 230, 25.0, 15.2, "Yes", 8.3, 95.0, 0.5],
    ])
    col_map = detect_sensor_columns(df, FIXED, REMAINING)
    result = apply_column_map(df, col_map)
    assert "dissolved_oxygen" in result.columns
    assert 5 not in result.columns
