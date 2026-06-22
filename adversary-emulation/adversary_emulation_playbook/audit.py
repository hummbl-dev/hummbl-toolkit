"""HUMMBL governance primitive wrappers for adversary emulation.

Integrates audit_log, delegation_token, and kill_switch from
hummbl-governance into the emulation lifecycle.
"""

from __future__ import annotations

import hashlib
import json
import pathlib
import time
import uuid
from dataclasses import dataclass, field
from typing import Any

from hummbl_governance.audit_log import AuditLog
from hummbl_governance.delegation import (
    DelegationTokenManager,
    TokenBinding,
)
from hummbl_governance.kill_switch import KillSwitch, KillSwitchMode


@dataclass(frozen=True)
class EmulationReceipt:
    """Immutable receipt for a single emulation action."""

    timestamp: float
    emulation_id: str
    token_id: str
    technique_id: str
    tactic: str
    status: str  # started, completed, halted, failed
    detail: dict[str, Any]
    sha256: str = field(init=False)

    def __post_init__(self) -> None:
        content = json.dumps(
            {
                "timestamp": self.timestamp,
                "emulation_id": self.emulation_id,
                "token_id": self.token_id,
                "technique_id": self.technique_id,
                "tactic": self.tactic,
                "status": self.status,
                "detail": self.detail,
            },
            sort_keys=True,
            separators=(",", ":"),
        )
        object.__setattr__(
            self, "sha256", hashlib.sha256(content.encode()).hexdigest()
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "emulation_id": self.emulation_id,
            "token_id": self.token_id,
            "technique_id": self.technique_id,
            "tactic": self.tactic,
            "status": self.status,
            "detail": self.detail,
            "sha256": self.sha256,
        }


class EmulationAuditor:
    """Wraps HUMMBL governance primitives for adversary emulation safety.

    Every emulation step is logged, scoped by delegation token, and
    subject to kill-switch halt.
    """

    LAB_HOSTS: frozenset[str] = frozenset({"localhost", "127.0.0.1", "::1"})

    def __init__(
        self,
        audit_base_dir: pathlib.Path | str | None = None,
        max_chain_depth: int = 5,
        token_expiry_minutes: int = 60,
    ) -> None:
        if audit_base_dir is None:
            audit_base_dir = pathlib.Path.cwd() / ".aep_audit"
            audit_base_dir.mkdir(exist_ok=True)
        self.audit_log = AuditLog(str(audit_base_dir))
        self.dtm = DelegationTokenManager()
        self.kill_switch = KillSwitch()
        self._token_expiry = token_expiry_minutes
        self._receipts: list[EmulationReceipt] = []
        self._chain_depth = 0
        self._max_chain_depth = max_chain_depth

    @property
    def state(self) -> str:
        """Current kill-switch mode name."""
        return self.kill_switch.mode.name

    def check_safety(self, target_hosts: tuple[str, ...]) -> None:
        """Verify emulation targets are lab-only. Engages kill switch otherwise."""
        if self.kill_switch.engaged:
            raise EmulationHalted(
                f"Kill switch is {self.state}; emulation cannot proceed"
            )
        for host in target_hosts:
            if host not in self.LAB_HOSTS:
                self.kill_switch.engage(
                    KillSwitchMode.EMERGENCY,
                    reason=f"non_lab_target: {host}",
                    triggered_by="EmulationAuditor.check_safety",
                )
                self._log_receipt(
                    emulation_id="safety_check",
                    token_id="none",
                    technique_id="none",
                    tactic="safety",
                    status="halted",
                    detail={"reason": f"non_lab_target: {host}", "action": "EMERGENCY"},
                )
                raise EmulationHalted(
                    f"Non-lab target detected: {host}. Kill switch engaged to EMERGENCY."
                )

    def begin_emulation(self, emulation_id: str) -> str:
        """Issue a delegation token and log the emulation start."""
        if self._chain_depth >= self._max_chain_depth:
            raise EmulationHalted(
                f"Max chain depth {self._max_chain_depth} exceeded"
            )
        self._chain_depth += 1

        binding = TokenBinding(
            task_id=emulation_id,
            contract_id="adversary-emulation-playbook",
        )
        token = self.dtm.create_token(
            issuer="aep-engine",
            subject=emulation_id,
            ops_allowed=["emulate", "audit", "halt"],
            binding=binding,
            expiry_minutes=self._token_expiry,
        )
        token_id = str(token.token_id)
        self._log_receipt(
            emulation_id=emulation_id,
            token_id=token_id,
            technique_id="none",
            tactic="orchestration",
            status="started",
            detail={"max_chain_depth": self._max_chain_depth, "chain_depth": self._chain_depth},
        )
        return token_id

    def record_step(
        self,
        *,
        emulation_id: str,
        token_id: str,
        technique_id: str,
        tactic: str,
        status: str,
        detail: dict[str, Any] | None = None,
    ) -> EmulationReceipt:
        """Record a single emulation step."""
        return self._log_receipt(
            emulation_id=emulation_id,
            token_id=token_id,
            technique_id=technique_id,
            tactic=tactic,
            status=status,
            detail=detail or {},
        )

    def end_emulation(
        self,
        emulation_id: str,
        token_id: str,
        summary: dict[str, Any],
    ) -> EmulationReceipt:
        """Log emulation completion."""
        receipt = self._log_receipt(
            emulation_id=emulation_id,
            token_id=token_id,
            technique_id="none",
            tactic="orchestration",
            status="completed",
            detail=summary,
        )
        self._chain_depth = max(0, self._chain_depth - 1)
        return receipt

    def get_receipts(self) -> tuple[EmulationReceipt, ...]:
        """Return all receipts for this session."""
        return tuple(self._receipts)

    def export_jsonl(self, path: str) -> None:
        """Export receipts as newline-delimited JSON."""
        with open(path, "w", encoding="utf-8") as f:
            for r in self._receipts:
                f.write(json.dumps(r.to_dict()) + "\n")

    def _log_receipt(
        self,
        emulation_id: str,
        token_id: str,
        technique_id: str,
        tactic: str,
        status: str,
        detail: dict[str, Any],
    ) -> EmulationReceipt:
        receipt = EmulationReceipt(
            timestamp=time.time(),
            emulation_id=emulation_id,
            token_id=token_id,
            technique_id=technique_id,
            tactic=tactic,
            status=status,
            detail=detail,
        )
        self._receipts.append(receipt)
        # Append to HUMMBL governance audit log
        self.audit_log.append(
            intent_id=emulation_id,
            task_id=technique_id or "orchestration",
            tuple_type="emulation_step",
            tuple_data=receipt.to_dict(),
            capability_token_id=token_id if token_id != "none" else None,
        )
        return receipt


class EmulationHalted(Exception):
    """Raised when emulation cannot proceed due to safety constraints."""
