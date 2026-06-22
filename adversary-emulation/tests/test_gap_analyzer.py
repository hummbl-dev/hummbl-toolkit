"""Tests for the gap analyzer."""

from __future__ import annotations

from adversary_emulation_playbook.emulate import EmulationReport, EmulationResult
from adversary_emulation_playbook.gap_analyzer import GapAnalyzer, GapReport
from adversary_emulation_playbook.playbook_loader import EmulationStep


class TestGapAnalyzer:
    def test_all_detected_no_gaps(self) -> None:
        step = EmulationStep(
            technique_id="T1566.001",
            technique_name="Spearphishing",
            tactic="initial-access",
            description="Test",
            expected_detection=["sigma_1"],
        )
        report = EmulationReport(
            playbook_id="test",
            threat_actor="Actor",
            results=[EmulationResult(step=step, status="detected")],
            coverage=1.0,
        )
        analyzer = GapAnalyzer()
        gap_report = analyzer.analyze(report)
        assert len(gap_report.gaps) == 0
        assert gap_report.coverage_score == 1.0
        assert gap_report.risk_score == 0.0

    def test_missed_creates_gap(self) -> None:
        step = EmulationStep(
            technique_id="T1566.001",
            technique_name="Spearphishing",
            tactic="initial-access",
            description="Test",
            expected_detection=["sigma_1"],
        )
        report = EmulationReport(
            playbook_id="test",
            threat_actor="Actor",
            results=[EmulationResult(step=step, status="missed")],
            coverage=0.0,
        )
        analyzer = GapAnalyzer()
        gap_report = analyzer.analyze(report)
        assert len(gap_report.gaps) == 1
        gap = gap_report.gaps[0]
        assert gap.technique_id == "T1566.001"
        assert gap.severity == "critical"
        assert gap.base120_transform == "P"
        assert "sigma_1" in gap.recommendation

    def test_gap_severity_by_tactic(self) -> None:
        # persistence -> high
        step = EmulationStep(
            technique_id="T1053.005",
            technique_name="Scheduled Task",
            tactic="persistence",
            description="Test",
            expected_detection=["sigma_1"],
        )
        report = EmulationReport(
            playbook_id="test",
            threat_actor="Actor",
            results=[EmulationResult(step=step, status="missed")],
        )
        analyzer = GapAnalyzer()
        gap_report = analyzer.analyze(report)
        assert gap_report.gaps[0].severity == "high"
        assert gap_report.gaps[0].base120_transform == "RE"

    def test_risk_score_computation(self) -> None:
        steps = [
            EmulationStep(
                technique_id="T1566.001",
                technique_name="Spearphishing",
                tactic="initial-access",
                description="Test",
                expected_detection=["sigma_1"],
            ),
            EmulationStep(
                technique_id="T1078",
                technique_name="Valid Accounts",
                tactic="privilege-escalation",
                description="Test",
                expected_detection=["sigma_2"],
            ),
        ]
        report = EmulationReport(
            playbook_id="test",
            threat_actor="Actor",
            results=[
                EmulationResult(step=steps[0], status="missed"),
                EmulationResult(step=steps[1], status="missed"),
            ],
        )
        analyzer = GapAnalyzer()
        gap_report = analyzer.analyze(report)
        # Both critical = 4.0 each, max 8.0, risk = 1.0
        assert gap_report.risk_score == 1.0

    def test_summary_for_defenders(self) -> None:
        step = EmulationStep(
            technique_id="T1566.001",
            technique_name="Spearphishing",
            tactic="initial-access",
            description="Test",
            expected_detection=["sigma_1"],
        )
        report = EmulationReport(
            playbook_id="test",
            threat_actor="Actor",
            results=[EmulationResult(step=step, status="missed")],
        )
        analyzer = GapAnalyzer()
        gap_report = analyzer.analyze(report)
        summary = analyzer.summarize_for_defenders(gap_report)
        assert "Gap Analysis: Actor" in summary
        assert "T1566.001" in summary
        assert "Base120: P" in summary

    def test_gap_report_dict(self) -> None:
        step = EmulationStep(
            technique_id="T1566.001",
            technique_name="Spearphishing",
            tactic="initial-access",
            description="Test",
            expected_detection=["sigma_1"],
        )
        report = EmulationReport(
            playbook_id="test",
            threat_actor="Actor",
            results=[EmulationResult(step=step, status="missed")],
        )
        analyzer = GapAnalyzer()
        gap_report = analyzer.analyze(report)
        d = gap_report.to_dict()
        assert d["playbook_id"] == "test"
        assert d["total_gaps"] == 1
        assert d["critical_gaps"] == 1
        assert "gaps" in d
