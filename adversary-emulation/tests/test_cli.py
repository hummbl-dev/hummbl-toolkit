"""Tests for the CLI."""

from __future__ import annotations

import json
import pathlib
import tempfile

from adversary_emulation_playbook.cli import main


class TestCLI:
    def test_list_command(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            # Create a test playbook
            pathlib.Path(td) / "test.yaml"
            (pathlib.Path(td) / "test.yaml").write_text(
                "id: test\n"
                "threat_actor: Actor\n"
                "description: Test\n"
                "steps:\n"
                "  - technique_id: T1566.001\n"
                "    technique_name: Spearphishing\n"
                "    tactic: initial-access\n"
                "    description: Test\n"
            )
            exit_code = main(["list", "--playbook-dir", td])
            assert exit_code == 0

    def test_validate_command(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            pathlib.Path(td) / "test.yaml"
            (pathlib.Path(td) / "test.yaml").write_text(
                "id: test\n"
                "threat_actor: Actor\n"
                "description: Test\n"
                "steps:\n"
                "  - technique_id: T1566.001\n"
                "    technique_name: Spearphishing\n"
                "    tactic: initial-access\n"
                "    description: Test\n"
            )
            exit_code = main(["validate", "test", "--playbook-dir", td])
            assert exit_code == 0

    def test_run_command(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            pathlib.Path(td) / "test.yaml"
            (pathlib.Path(td) / "test.yaml").write_text(
                "id: test\n"
                "threat_actor: Actor\n"
                "description: Test\n"
                "steps:\n"
                "  - technique_id: T1566.001\n"
                "    technique_name: Spearphishing\n"
                "    tactic: initial-access\n"
                "    description: Test\n"
            )
            out_path = str(pathlib.Path(td) / "output.json")
            exit_code = main(
                ["run", "test", "--playbook-dir", td, "--output", out_path]
            )
            assert exit_code == 0
            with open(out_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            assert "emulation_report" in data

    def test_run_with_gap_analysis(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            pathlib.Path(td) / "test.yaml"
            (pathlib.Path(td) / "test.yaml").write_text(
                "id: test\n"
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
            out_path = str(pathlib.Path(td) / "output.json")
            exit_code = main(
                [
                    "run",
                    "test",
                    "--playbook-dir",
                    td,
                    "--output",
                    out_path,
                    "--gap-analysis",
                ]
            )
            assert exit_code == 0
            with open(out_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            assert "gap_analysis" in data

    def test_validate_failure(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            exit_code = main(["validate", "missing", "--playbook-dir", td])
            assert exit_code == 1

    def test_run_with_detection_rules(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            pathlib.Path(td) / "test.yaml"
            (pathlib.Path(td) / "test.yaml").write_text(
                "id: test\n"
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
            rules_path = str(pathlib.Path(td) / "rules.json")
            with open(rules_path, "w", encoding="utf-8") as f:
                json.dump({"T1566.001": ["sigma_1"]}, f)
            out_path = str(pathlib.Path(td) / "output.json")
            exit_code = main(
                [
                    "run",
                    "test",
                    "--playbook-dir",
                    td,
                    "--detection-rules",
                    rules_path,
                    "--output",
                    out_path,
                ]
            )
            assert exit_code == 0
            with open(out_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            assert data["emulation_report"]["detection_rate"] == 1.0
