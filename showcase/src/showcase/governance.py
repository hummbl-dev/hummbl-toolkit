"""Governance primitive wiring for the showcase."""

from __future__ import annotations

from hummbl_governance import CircuitBreaker, CostGovernor, KillSwitch, KillSwitchMode

from showcase.adapters import (
    MockCalendarAdapter,
    MockCostTracker,
    MockGitHubAdapter,
    MockLinearAdapter,
)
from showcase.bus import InMemoryBus


class GovernanceStack:
    """Wires hummbl-governance primitives around mock adapters."""

    def __init__(self, bus: InMemoryBus) -> None:
        self.bus = bus
        self.kill_switch = KillSwitch()
        self.circuit_breaker = CircuitBreaker(failure_threshold=3, recovery_timeout=30.0)
        self.cost_governor = CostGovernor(":memory:", soft_cap=50.0, hard_cap=100.0)

        self.adapters = {
            "github": MockGitHubAdapter(failure_rate=0.0),
            "calendar": MockCalendarAdapter(failure_rate=0.0),
            "linear": MockLinearAdapter(failure_rate=0.0),
            "cost": MockCostTracker(failure_rate=0.0),
        }

    def check_kill_switch(self) -> str:
        """Return kill switch status."""
        return self.kill_switch.mode.name

    def check_circuit(self, name: str) -> str:
        """Return circuit breaker state for an adapter."""
        return self.circuit_breaker.state.name

    def record_cost(self, provider: str, model: str, cost: float) -> dict:
        """Record API usage and return budget status."""
        self.cost_governor.record_usage(
            provider=provider,
            model=model,
            tokens_in=1000,
            tokens_out=500,
            cost=cost,
        )
        return self.cost_governor.check_budget_status().to_dict()

    def run_health_checks(self) -> list[dict]:
        """Run health checks on all adapters."""
        results = []
        for name, adapter in self.adapters.items():
            try:
                result = adapter.health_check()
                results.append({
                    "adapter": name,
                    "status": result.get("status", "unknown"),
                    "latency_ms": result.get("latency_ms", 0),
                })
            except Exception as e:
                results.append({
                    "adapter": name,
                    "status": "unhealthy",
                    "latency_ms": 0,
                    "error": str(e),
                })
        return results

    def engage_kill_switch(self, mode: KillSwitchMode, reason: str) -> None:
        """Engage kill switch for demo purposes."""
        self.kill_switch.engage(
            mode=mode,
            reason=reason,
            triggered_by="operator",
        )
        self.bus.post("operator", "all", "DECISION", f"Kill switch engaged: {mode.name} — {reason}")

    def disengage_kill_switch(self, reason: str) -> None:
        """Disengage kill switch."""
        self.kill_switch.disengage(
            reason=reason,
            triggered_by="operator",
        )
        self.bus.post("operator", "all", "DECISION", f"Kill switch disengaged — {reason}")
