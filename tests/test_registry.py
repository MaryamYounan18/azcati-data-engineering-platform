import pytest
from pathlib import Path
from datetime import date
from tempfile import TemporaryDirectory
from registry.experiment_registry import Experiment, ExperimentRegistry


def make_registry(tmp):
    return ExperimentRegistry(Path(tmp) / "test.sqlite")


def test_register_and_coverage():
    with TemporaryDirectory() as tmp:
        reg = make_registry(tmp)
        reg.register(Experiment(
            experiment_id="EXP_001",
            strain_name="Chlorella vulgaris",
            start_date=date(2023, 1, 1),
            end_date=date(2023, 1, 30),
            reactors=["R1"],
        ))
        reg.ingest_readings("EXP_001", "R1", "do",
                            ["2023-01-01T08:00", "2023-01-01T08:15"],
                            [8.2, 8.5])
        coverage = reg.sensor_coverage("EXP_001")
        assert coverage["R1"]["do"] == 2


def test_duplicate_detection():
    with TemporaryDirectory() as tmp:
        reg = make_registry(tmp)
        reg.register(Experiment(
            experiment_id="EXP_A",
            strain_name="Chlorella vulgaris",
            start_date=date(2023, 6, 1),
            end_date=date(2023, 6, 30),
            reactors=["R1"],
        ))
        reg.register(Experiment(
            experiment_id="EXP_B",
            strain_name="Chlorella vulgaris",
            start_date=date(2023, 6, 15),
            end_date=date(2023, 7, 15),
            reactors=["R1"],
        ))
        dupes = reg.find_duplicate_candidates()
        assert len(dupes) >= 1
