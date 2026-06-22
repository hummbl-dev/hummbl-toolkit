"""Tests for playbook loading and validation."""

from __future__ import annotations

import pathlib
import tempfile

import pytest

from adversary_emulation_playbook.playbook_loader import (
    EmulationStep,
    Playbook,
    PlaybookLoader,
)


class TestEmulationStep:
    def test_from_dict_minimal(self) -> None:
        data = {
            "technique_id": "T1566.001",
            "technique_name": "Spearphishing Attachment",
            "tactic": "initial-access",
            "description": "Test",
        }
        step = EmulationStep.from_dict(data)
        assert step.technique_id == "T1566.001"
        assert step.lab_only is True
        assert step.target_hosts == ()

    def test_from_dict_full(self) -> None:
        data = {
            "technique_id": "T1053.005",
            "technique_name": "Scheduled Task",
            "tactic": "persistence",
            "description": "Test desc",
            "expected_detection": ["sigma_1", "sigma_2"],
            "lab_only": False,
            "target_hosts": ["host1"],
        }
        step = EmulationStep.from_dict(data)
        assert step.lab_only is False
        assert step.target_hosts == ("host1",)
        assert step.expected_detection == ["sigma_1", "sigma_2"]

    def test_to_dict_roundtrip(self) -> None:
        step = EmulationStep(
            technique_id="T1078",
            technique_name="Valid Accounts",
            tactic="privilege-escalation",
            description="Test",
            expected_detection=["sigma_a"],
            lab_only=True,
            target_hosts=(),
        )
        data = step.to_dict()
        restored = EmulationStep.from_dict(data)
        assert restored == step


class TestPlaybook:
    def test_from_dict(self) -> None:
        data = {
            "id": "test-playbook",
            "threat_actor": "TestActor",
            "description": "A test",
            "mitre_version": "14.1",
            "steps": [
                {
                    "technique_id": "T1566.001",
                    "technique_name": "Spearphishing",
                    "tactic": "initial-access",
                    "description": "Test",
                }
            ],
        }
        pb = Playbook.from_dict(data)
        assert pb.id == "test-playbook"
        assert len(pb.steps) == 1
        assert pb.steps[0].technique_id == "T1566.001"


class TestPlaybookLoader:
    def test_load_yaml_minimal(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            path = pathlib.Path(td) / "test.yaml"
            path.write_text(
                "id: test\n"
                "threat_actor: Actor\n"
                "description: Test\n"
                "steps:\n"
                "  - technique_id: T1566.001\n"
                "    technique_name: Spearphishing\n"
                "    tactic: initial-access\n"
                "    description: Test desc\n"
            )
            loader = PlaybookLoader(td)
            pb = loader.load("test")
            assert pb.id == "test"
            assert len(pb.steps) == 1

    def test_load_json(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            path = pathlib.Path(td) / "test.json"
            import json

            path.write_text(
                json.dumps(
                    {
                        "id": "json-test",
                        "threat_actor": "Actor",
                        "description": "Test",
                        "steps": [],
                    }
                )
            )
            loader = PlaybookLoader(td)
            pb = loader.load("test")
            assert pb.id == "json-test"

    def test_list_playbooks(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            (pathlib.Path(td) / "a.yaml").write_text("id: a\nthreat_actor: A\nsteps: []")
            (pathlib.Path(td) / "b.yml").write_text("id: b\nthreat_actor: B\nsteps: []")
            loader = PlaybookLoader(td)
            names = loader.list_playbooks()
            assert names == ["a", "b"]

    def test_missing_playbook(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            loader = PlaybookLoader(td)
            with pytest.raises(FileNotFoundError):
                loader.load("missing")
