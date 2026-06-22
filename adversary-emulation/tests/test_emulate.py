"""Tests for the core emulation engine."""

from __future__ import annotations

import tempfile

import pytest

from adversary_emulation_playbook.emulate import EmulationEngine, EmulationResult
from adversary_emulation_playbook.audit import EmulationHalted
from adversary_emulation_playbook.playbook_loader import EmulationStep


class TestEmulationEngine:
    def test_run_with_no_detections(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            engine = EmulationEngine(td)
            # Create a minimal playbook
            import pathlib

            pb_path = pathlib.Path(td) / "mini.yaml"
            pb_path.write_text(
                "id: mini\n"
                "threat_actor: MiniActor\n"
                "description: Test\n"
                "steps:\n"
                "  - technique_id: T1566.001\n"
                "    technique_name: Spearphishing\n"
                "    tactic: initial-access\n"
                "    description: Test\n"
                "    expected_detection:\n"
                "      - sigma_1\n"
            )
            report = engine.run("mini")
            assert report.playbook_id == "mini"
            assert len(report.results) == 1
            assert report.results[0].status == "missed"
            assert report.detection_rate == 0.0
            assert report.coverage == 0.0
            assert not report.halted

    def test_run_with_detection(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            engine = EmulationEngine(td)
            import pathlib

            pb_path = pathlib.Path(td) / "detected.yaml"
            pb_path.write_text(
                "id: detected\n"
                "threat_actor: Actor\n"
                "description: Test\n"
                "steps:\n"
                "  - technique_id: T1566.001\n"
                "    technique_name: Spearphishing\n"
                "    tactic: initial-access\n"
                "    description: Test\n"
                "    expected_detection:\n"
                "      - sigma_1\n"
            )
            report = engine.run(
                "detected",
                detection_rules={"T1566.001": ["sigma_1"]},
            )
            assert report.results[0].status == "detected"
            assert report.detection_rate == 1.0
            assert report.coverage == 1.0

    def test_halt_on_non_lab_target(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            engine = EmulationEngine(td)
            import pathlib

            pb_path = pathlib.Path(td) / "unsafe.yaml"
            pb_path.write_text(
                "id: unsafe\n"
                "threat_actor: BadActor\n"
                "description: Test\n"
                "steps:\n"
                "  - technique_id: T1566.001\n"
                "    technique_name: Spearphishing\n"
                "    tactic: initial-access\n"
                "    description: Test\n"
                "    target_hosts:\n"
                "      - evil.com\n"
            )
            report = engine.run("unsafe")
            assert report.halted
            assert "evil.com" in report.halt_reason
            assert len(report.results) == 0

    def test_receipts_generated(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            engine = EmulationEngine(td)
            import pathlib

            pb_path = pathlib.Path(td) / "receipt.yaml"
            pb_path.write_text(
                "id: receipt\n"
                "threat_actor: Actor\n"
                "description: Test\n"
                "steps:\n"
                "  - technique_id: T1566.001\n"
                "    technique_name: Spearphishing\n"
                "    tactic: initial-access\n"
                "    description: Test\n"
            )
            report = engine.run("receipt")
            assert len(report.receipts) >= 3  # start, step start, step end, complete
            # Verify all receipts have sha256
            for r in report.receipts:
                assert "sha256" in r
                assert len(r["sha256"]) == 64

    def test_report_dict(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            engine = EmulationEngine(td)
            import pathlib

            pb_path = pathlib.Path(td) / "dict.yaml"
            pb_path.write_text(
                "id: dict\n"
                "threat_actor: Actor\n"
                "description: Test\n"
                "steps:\n"
                "  - technique_id: T1566.001\n"
                "    technique_name: Spearphishing\n"
                "    tactic: initial-access\n"
                "    description: Test\n"
            )
            report = engine.run("dict")
            d = report.to_dict()
            assert d["playbook_id"] == "dict"
            assert "detection_rate" in d
            assert isinstance(d["detection_rate"], float)


class TestEmulationResult:
    def test_detected_property(self) -> None:
        step = EmulationStep(
            technique_id="T1566.001",
            technique_name="Spearphishing",
            tactic="initial-access",
            description="Test",
            expected_detection=["sigma_1"],
        )
        result = EmulationResult(step=step, status="detected")
        assert result.detected is True

        result2 = EmulationResult(step=step, status="missed")
        assert result2.detected is False
