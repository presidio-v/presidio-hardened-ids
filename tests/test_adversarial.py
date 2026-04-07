"""Tests for adversarial evasion and retraining."""

import json

from presidio_ids.adversarial import EvasionReport, load_adversarial_flows, run_evasion
from presidio_ids.traffic import LABEL_COL


def test_run_evasion_returns_report(fitted_detector, tmp_path, small_df):
    model_path = str(tmp_path / "model.pkl")
    fitted_detector.save(model_path)
    report_path = str(tmp_path / "evasion.json")

    report = run_evasion(
        model_path=model_path,
        attack_type="portscan",
        n_attempts=20,
        output=report_path,
    )
    assert isinstance(report, EvasionReport)
    assert report.n_attempts == 20
    assert 0.0 <= report.evasion_rate <= 1.0


def test_run_evasion_saves_json(fitted_detector, tmp_path):
    model_path = str(tmp_path / "model.pkl")
    fitted_detector.save(model_path)
    report_path = str(tmp_path / "evasion.json")

    run_evasion(model_path=model_path, attack_type="synflood", n_attempts=10, output=report_path)
    with open(report_path) as f:
        data = json.load(f)
    assert "evasion_rate" in data
    assert "evaded_flows" in data


def test_load_adversarial_flows_empty(tmp_path):
    path = str(tmp_path / "empty.json")
    with open(path, "w") as f:
        json.dump({"evaded_flows": []}, f)
    df = load_adversarial_flows(path)
    assert df.empty


def test_load_adversarial_flows_with_data(fitted_detector, tmp_path):
    model_path = str(tmp_path / "model.pkl")
    fitted_detector.save(model_path)
    report_path = str(tmp_path / "evasion.json")

    report = run_evasion(
        model_path=model_path,
        attack_type="portscan",
        n_attempts=50,
        output=report_path,
    )
    if report.n_evaded > 0:
        df = load_adversarial_flows(report_path)
        assert len(df) == report.n_evaded
        assert LABEL_COL in df.columns
