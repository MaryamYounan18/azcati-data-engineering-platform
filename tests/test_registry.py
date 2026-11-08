import pytest
from pathlib import Path
from tempfile import TemporaryDirectory
from registry.experiment_registry import ExperimentRegistry

def test_register_and_coverage():
    with TemporaryDirectory() as tmp:
        reg = ExperimentRegistry(Path(tmp) / "test.sqlite")
        reg.register("EXP_001", start="2023-01-01", end="2023-01-30")
        
        readings = [
            {"timestamp": "2023-01-01T08:00", "pond": "R1", "do": 8.2, "temp": 22.1},
            {"timestamp": "2023-01-01T08:15", "pond": "R1", "do": 8.5, "temp": 22.3},
        ]
        reg.ingest_readings("EXP_001", readings)
        
        coverage = reg.sensor_coverage("EXP_001")
        assert coverage["R1"]["do"] == 2
        assert coverage["R1"]["temp"] == 2

def test_duplicate_detection():
    with TemporaryDirectory() as tmp:
        reg = ExperimentRegistry(Path(tmp) / "test.sqlite")
        reg.register("EXP_A", start="2023-06-01", end="2023-06-30")
        reg.register("EXP_B", start="2023-06-15", end="2023-07-15")
        
        dupes = reg.find_duplicate_candidates()
        assert len(dupes) >= 1
