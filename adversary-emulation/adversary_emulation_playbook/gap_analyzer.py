"""Analyze detection coverage gaps after adversary emulation runs."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .emulate import EmulationReport


@dataclass(frozen=True)
class Gap:
    """A single detection gap identified during analysis."""

    technique_id: str
    technique_name: str
    tactic: str
    gap_type: str  # missing_rule, incomplete_rule, no_expected_rules
    severity: str  # critical, high, medium, low
    recommendation: str
    base120_transform: str  # Which Base120 transform applies

    def to_dict(self) -> dict[str, Any]:
        return {
            "technique_id": self.technique_id,
            "technique_name": self.technique_name,
            "tactic": self.tactic,
            "gap_type": self.gap_type,
            "severity": self.severity,
            "recommendation": self.recommendation,
            "base120_transform": self.base120_transform,
        }


@dataclass
class GapReport:
    """Comprehensive gap analysis for a playbook."""

    playbook_id: str
    threat_actor: str
    gaps: list[Gap] = field(default_factory=list)
    coverage_score: float = 0.0
    risk_score: float = 0.0

    @property
    def critical_gaps(self) -> list[Gap]:
        return [g for g in self.gaps if g.severity == "critical"]

    @property
    def high_gaps(self) -> list[Gap]:
        return [g for g in self.gaps if g.severity == "high"]

    def to_dict(self) -> dict[str, Any]:
        return {
            "playbook_id": self.playbook_id,
            "threat_actor": self.threat_actor,
            "coverage_score": round(self.coverage_score, 4),
            "risk_score": round(self.risk_score, 4),
            "total_gaps": len(self.gaps),
            "critical_gaps": len(self.critical_gaps),
            "high_gaps": len(self.high_gaps),
            "gaps": [g.to_dict() for g in self.gaps],
        }


class GapAnalyzer:
    """Analyze emulation reports to identify detection coverage gaps.

    Uses Base120 mental models to frame recommendations:
    - P (Problem): What attack surface is exposed?
    - IN (Insight): What detection logic is missing?
    - CO (Comparison): How do other organizations detect this?
    - DE (Design): What rule or control should be built?
    - RE (Recursion): What sub-techniques are also uncovered?
    - SY (Synthesis): How do gaps combine into kill chains?
    """

    SEVERITY_MAP: dict[str, str] = {
        "initial-access": "critical",
        "execution": "critical",
        "persistence": "high",
        "privilege-escalation": "critical",
        "defense-evasion": "high",
        "credential-access": "critical",
        "discovery": "medium",
        "lateral-movement": "critical",
        "collection": "medium",
        "exfiltration": "high",
        "command-and-control": "high",
    }

    TRANSFORM_MAP: dict[str, str] = {
        "initial-access": "P",  # Problem: attack surface
        "execution": "DE",  # Design: execution controls
        "persistence": "RE",  # Recursion: backdoors, sub-techniques
        "privilege-escalation": "P",  # Problem: elevated access surface
        "defense-evasion": "IN",  # Insight: what are we not seeing?
        "credential-access": "CO",  # Comparison: credential monitoring
        "discovery": "IN",  # Insight: reconnaissance visibility
        "lateral-movement": "SY",  # Synthesis: kill chain combination
        "collection": "RE",  # Recursion: data staging
        "exfiltration": "CO",  # Comparison: DLP/egress monitoring
        "command-and-control": "SY",  # Synthesis: C2 as system behavior
    }

    def analyze(self, report: EmulationReport) -> GapReport:
        """Analyze an emulation report and produce a gap analysis."""
        gap_report = GapReport(
            playbook_id=report.playbook_id,
            threat_actor=report.threat_actor,
            coverage_score=report.coverage,
        )

        for result in report.results:
            step = result.step
            if result.status == "detected":
                continue  # No gap

            severity = self.SEVERITY_MAP.get(step.tactic, "medium")
            transform = self.TRANSFORM_MAP.get(step.tactic, "P")

            if result.status == "missed":
                if not step.expected_detection:
                    gap_type = "no_expected_rules"
                    recommendation = (
                        f"Research detection methods for {step.technique_id}. "
                        "No expected rules defined in playbook."
                    )
                else:
                    gap_type = "missing_rule"
                    recommendation = (
                        f"Deploy detection rules for {step.technique_id}: "
                        f"{', '.join(step.expected_detection)}"
                    )
            else:
                gap_type = "incomplete_rule"
                recommendation = (
                    f"Review and extend detection coverage for {step.technique_id}. "
                    f"Current rules may not cover all variants."
                )

            gap = Gap(
                technique_id=step.technique_id,
                technique_name=step.technique_name,
                tactic=step.tactic,
                gap_type=gap_type,
                severity=severity,
                recommendation=recommendation,
                base120_transform=transform,
            )
            gap_report.gaps.append(gap)

        # Compute risk score: weighted by severity
        weights = {"critical": 4.0, "high": 2.0, "medium": 1.0, "low": 0.5}
        total_weight = sum(weights.get(g.severity, 1.0) for g in gap_report.gaps)
        max_possible = len(report.results) * 4.0  # All critical
        gap_report.risk_score = (
            total_weight / max_possible if max_possible else 0.0
        )

        return gap_report

    def summarize_for_defenders(self, gap_report: GapReport) -> str:
        """Generate a human-readable summary for blue teams."""
        lines = [
            f"# Gap Analysis: {gap_report.threat_actor}",
            "",
            f"- Coverage Score: {gap_report.coverage_score:.1%}",
            f"- Risk Score: {gap_report.risk_score:.2f}",
            f"- Total Gaps: {len(gap_report.gaps)}",
            f"- Critical: {len(gap_report.critical_gaps)} | High: {len(gap_report.high_gaps)}",
            "",
            "## Priority Actions",
        ]

        for gap in gap_report.critical_gaps[:5]:
            lines.append(
                f"- **[{gap.technique_id}] {gap.technique_name}** "
                f"({gap.tactic}) — {gap.recommendation} "
                f"[Base120: {gap.base120_transform}]"
            )

        if len(gap_report.critical_gaps) > 5:
            lines.append(
                f"- ... and {len(gap_report.critical_gaps) - 5} more critical gaps"
            )

        return "\n".join(lines)
