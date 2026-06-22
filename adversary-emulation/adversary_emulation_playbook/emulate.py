"""Core adversary emulation engine with HUMMBL governance integration."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .audit import EmulationAuditor, EmulationHalted
from .playbook_loader import EmulationStep, Playbook, PlaybookLoader


@dataclass(frozen=True)
class EmulationResult:
    """Result of a single emulation step."""

    step: EmulationStep
    status: str  # simulated, detected, missed, halted
    detail: dict[str, Any] = field(default_factory=dict)

    @property
    def detected(self) -> bool:
        return self.status == "detected"


@dataclass
class EmulationReport:
    """Full report for a playbook emulation run."""

    playbook_id: str
    threat_actor: str
    results: list[EmulationResult] = field(default_factory=list)
    receipts: list[dict[str, Any]] = field(default_factory=list)
    coverage: float = 0.0
    halted: bool = False
    halt_reason: str = ""

    @property
    def techniques_tested(self) -> int:
        return len(self.results)

    @property
    def techniques_detected(self) -> int:
        return sum(1 for r in self.results if r.detected)

    @property
    def detection_rate(self) -> float:
        if not self.results:
            return 0.0
        return self.techniques_detected / len(self.results)

    def to_dict(self) -> dict[str, Any]:
        return {
            "playbook_id": self.playbook_id,
            "threat_actor": self.threat_actor,
            "techniques_tested": self.techniques_tested,
            "techniques_detected": self.techniques_detected,
            "detection_rate": round(self.detection_rate, 4),
            "coverage": round(self.coverage, 4),
            "halted": self.halted,
            "halt_reason": self.halt_reason,
            "results": [
                {
                    "technique_id": r.step.technique_id,
                    "status": r.status,
                    "detail": r.detail,
                }
                for r in self.results
            ],
        }


class EmulationEngine:
    """Execute adversary emulation playbooks with governance guarantees.

    Each emulation is scoped by a delegation token, logged to an append-only
    audit trail, and subject to emergency halt via kill switch. No emulation
    can target non-lab hosts.
    """

    def __init__(self, playbook_dir: str | None = None) -> None:
        self.loader = PlaybookLoader(playbook_dir)
        self.auditor = EmulationAuditor()

    def run(
        self,
        playbook_name: str,
        *,
        detection_rules: dict[str, list[str]] | None = None,
        simulate: bool = True,
    ) -> EmulationReport:
        """Run an emulation playbook.

        Args:
            playbook_name: Name of the playbook file (without extension)
            detection_rules: Mapping technique_id -> list of detection rule IDs
                             that are deployed. If None, no detections fire.
            simulate: If True, do not execute real actions (always True for safety)

        Returns:
            EmulationReport with coverage analysis and audit receipts
        """
        playbook = self.loader.load(playbook_name)
        report = EmulationReport(
            playbook_id=playbook.id,
            threat_actor=playbook.threat_actor,
        )

        # Begin governance session
        try:
            token = self.auditor.begin_emulation(playbook.id)
        except Exception as exc:
            report.halted = True
            report.halt_reason = f"governance_init_failed: {exc}"
            return report

        # Execute each step under governance
        for step in playbook.steps:
            try:
                result = self._run_step(
                    step,
                    emulation_id=playbook.id,
                    token_id=token,
                    detection_rules=detection_rules or {},
                    simulate=simulate,
                )
                report.results.append(result)
            except EmulationHalted as exc:
                report.halted = True
                report.halt_reason = str(exc)
                self.auditor.record_step(
                    emulation_id=playbook.id,
                    token_id=token,
                    technique_id=step.technique_id,
                    tactic=step.tactic,
                    status="halted",
                    detail={"reason": str(exc)},
                )
                break

        # Compute coverage: fraction of techniques with any detection rule present
        total = len(playbook.steps)
        covered = sum(
            1
            for s in playbook.steps
            if detection_rules and s.technique_id in detection_rules
        )
        report.coverage = covered / total if total else 0.0

        # End governance session
        summary = {
            "techniques_tested": report.techniques_tested,
            "techniques_detected": report.techniques_detected,
            "detection_rate": report.detection_rate,
            "coverage": report.coverage,
            "halted": report.halted,
        }
        self.auditor.end_emulation(playbook.id, token, summary)
        report.receipts = [r.to_dict() for r in self.auditor.get_receipts()]
        return report

    def _run_step(
        self,
        step: EmulationStep,
        *,
        emulation_id: str,
        token_id: str,
        detection_rules: dict[str, list[str]],
        simulate: bool,
    ) -> EmulationResult:
        """Run a single emulation step with safety checks."""
        # Safety: verify lab-only targets
        self.auditor.check_safety(step.target_hosts)

        # Safety: verify kill switch is disengaged
        if self.auditor.state != "DISENGAGED":
            raise EmulationHalted(
                f"Kill switch is {self.auditor.state}; cannot proceed with {step.technique_id}"
            )

        # Log step start
        self.auditor.record_step(
            emulation_id=emulation_id,
            token_id=token_id,
            technique_id=step.technique_id,
            tactic=step.tactic,
            status="started",
            detail={"simulate": simulate, "description": step.description},
        )

        # Simulate the technique (never executes real exploits)
        if simulate:
            status, detail = self._simulate_technique(step, detection_rules)
        else:
            # Real execution is intentionally unsupported in this version
            raise EmulationHalted(
                "Real execution is not supported. Use simulate=True."
            )

        # Log step completion
        self.auditor.record_step(
            emulation_id=emulation_id,
            token_id=token_id,
            technique_id=step.technique_id,
            tactic=step.tactic,
            status=status,
            detail=detail,
        )

        return EmulationResult(step=step, status=status, detail=detail)

    def _simulate_technique(
        self,
        step: EmulationStep,
        detection_rules: dict[str, list[str]],
    ) -> tuple[str, dict[str, Any]]:
        """Simulate a technique and determine if it would be detected.

        Simulation model (v0.1):
        - If the technique ID has a deployed detection rule -> "detected"
        - If the technique ID has no deployed rule -> "missed"
        - This is intentionally simple; future versions may add noise,
          evasion probability, and behavioral fidelity.
        """
        deployed = detection_rules.get(step.technique_id, [])
        expected = step.expected_detection

        # Coverage: did we have *any* rule for this technique?
        if not deployed:
            return "missed", {
                "reason": "no_detection_rule_deployed",
                "expected_rules": expected,
            }

        # Detection: do deployed rules cover the expected ones?
        matched = [r for r in expected if r in deployed]
        if matched:
            return "detected", {
                "reason": "expected_rule_matched",
                "matched_rules": matched,
                "all_deployed": deployed,
            }

        # Partial: we have a rule for the technique but not the specific variant
        return "missed", {
            "reason": "rule_present_but_not_expected_variant",
            "deployed_rules": deployed,
            "expected_rules": expected,
        }
