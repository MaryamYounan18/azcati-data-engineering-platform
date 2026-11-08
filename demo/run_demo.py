"""
End-to-end demo: load flagged CSV → detect column shift → filter faulty
data → store in registry → print coverage summary.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import pandas as pd
from datetime import date
from tempfile import TemporaryDirectory
from pathlib import Path
from sensor_qc.column_detector import detect_sensor_columns, apply_column_map
from sensor_qc.faulty_filter   import filter_faulty
from registry.experiment_registry import Experiment, ExperimentRegistry

FIXED_COLS = {0:"timestamp", 1:"reactor_id", 2:"pH", 3:"ORP",
              4:"temperature", 5:"conductivity"}
REMAINING  = ["dissolved_oxygen", "oxygen_saturation", "salinity"]
SENSORS    = ["pH", "ORP", "temperature", "conductivity",
              "dissolved_oxygen", "oxygen_saturation", "salinity"]
DATA_DIR   = os.path.join(os.path.dirname(__file__), "data")

def load_reactor(reactor_id):
    path = os.path.join(DATA_DIR, f"flagged_data_{reactor_id}.csv")
    raw  = pd.read_csv(path, header=0)
    raw.columns = range(len(raw.columns))
    col_map = detect_sensor_columns(raw, FIXED_COLS, REMAINING)
    df = apply_column_map(raw, col_map)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df["reactor_id"] = reactor_id
    return df

def main():
    with TemporaryDirectory() as tmp:
        registry = ExperimentRegistry(Path(tmp) / "demo.sqlite")
        registry.register(Experiment(
            experiment_id="DEMO_EXP_001",
            strain_name="Chlorella vulgaris",
            start_date=date(2024, 6, 1),
            end_date=date(2024, 6, 30),
            reactors=["R1", "R2"],
        ))

        for reactor_id in ["R1", "R2"]:
            print(f"\n── {reactor_id} ──")
            df = load_reactor(reactor_id)
            print(f"  Loaded {len(df):,} rows from flagged CSV")

            for sensor in SENSORS:
                if sensor not in df.columns:
                    continue
                sub = df[["timestamp", sensor]].dropna()
                ts_raw, val_raw = sub["timestamp"].tolist(), sub[sensor].tolist()
                ts_clean, val_clean = filter_faulty(ts_raw, val_raw, sensor)
                removed = len(ts_raw) - len(ts_clean)
                registry.ingest_readings("DEMO_EXP_001", reactor_id, sensor,
                                         ts_clean, val_clean)
                if removed:
                    print(f"  {sensor:22s}  {len(ts_raw):,} → {len(ts_clean):,}"
                          f"  ({removed} faulty removed)")

        print("\n── Coverage summary ──")
        for reactor, sensors in sorted(registry.sensor_coverage("DEMO_EXP_001").items()):
            print(f"  {reactor}:")
            for s, n in sensors.items():
                print(f"    {s:22s}  {n:,} readings")

if __name__ == "__main__":
    main()
