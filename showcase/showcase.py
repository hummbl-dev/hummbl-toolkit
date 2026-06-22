#!/usr/bin/env python3
"""founder-mode-showcase — Demo the HUMMBL agent mesh in 5 minutes.

Run: python showcase.py
"""

from __future__ import annotations

import json
import os
import sys

# Ensure src/ is on the path for the demo
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from showcase.adapters import (
    MockCalendarAdapter,
    MockCostTracker,
    MockGitHubAdapter,
    MockLinearAdapter,
)
from showcase.briefing import generate_briefing
from showcase.bus import InMemoryBus
from showcase.governance import GovernanceStack


def main() -> None:
    print("=" * 60)
    print("  founder-mode-showcase v0.1.0")
    print("  Demo the HUMMBL multi-agent governance mesh")
    print("=" * 60)
    print()

    # Initialize the coordination bus
    bus = InMemoryBus()
    bus.post("showcase", "all", "STATUS", "Showcase initialized")

    # Initialize governance stack (kill switch, circuit breaker, cost governor)
    gov = GovernanceStack(bus)
    bus.post("showcase", "all", "STATUS", "Governance stack initialized")

    # Run health checks on all adapters
    print("[1/5] Running health checks...")
    health = gov.run_health_checks()
    passing = sum(1 for h in health if h["status"] == "healthy")
    print(f"      {passing}/{len(health)} adapters healthy")
    for h in health:
        print(f"      • {h['adapter']}: {h['status']} ({h['latency_ms']}ms)")
    print()

    # Record some API costs (simulated)
    print("[2/5] Recording API usage...")
    gov.record_cost("anthropic", "claude-sonnet-4-6", 0.045)
    gov.record_cost("openai", "gpt-4o", 0.032)
    gov.record_cost("ollama", "qwen2.5-coder:3b", 0.001)
    status = gov.cost_governor.check_budget_status()
    cost_status = gov.cost_governor.check_budget_status()
    print(f"      Budget: ${cost_status.current_spend:.2f} / ${cost_status.hard_cap:.2f}")
    print(f"      Decision: {status.decision}")
    bus.post("showcase", "all", "STATUS", f"Cost check: {status.decision}")
    print()

    # Check kill switch status
    print("[3/5] Checking kill switch...")
    ks_status = gov.check_kill_switch()
    print(f"      Kill switch: {ks_status}")
    bus.post("showcase", "all", "STATUS", f"Kill switch: {ks_status}")
    print()

    # Check circuit breakers
    print("[4/5] Checking circuit breakers...")
    for name in gov.adapters:
        cb_status = gov.check_circuit(name)
        print(f"      • {name}: {cb_status}")
    bus.post("showcase", "all", "STATUS", "All circuits CLOSED")
    print()

    # Generate the morning briefing
    print("[5/5] Generating morning briefing...")
    print()
    briefing = generate_briefing(
        github=gov.adapters["github"],
        calendar=gov.adapters["calendar"],
        linear=gov.adapters["linear"],
        cost=gov.adapters["cost"],
        bus=bus,
        kill_switch_status=ks_status,
        circuit_states={name: gov.check_circuit(name) for name in gov.adapters},
        cost_status=gov.cost_governor.check_budget_status().to_dict(),
    )
    print(briefing)

    # Save to dashboard data file
    dashboard_data = {
        "briefing": briefing,
        "health": health,
        "kill_switch": ks_status,
        "circuits": {name: gov.check_circuit(name) for name in gov.adapters},
        "cost": {
            "spent": cost_status.current_spend,
            "budget": cost_status.hard_cap,
            "decision": cost_status.decision,
        },
        "bus_messages": len(bus),
    }
    dashboard_path = os.path.join(os.path.dirname(__file__), "dashboard", "data.json")
    with open(dashboard_path, "w") as f:
        json.dump(dashboard_data, f, indent=2)
    print(f"Dashboard data written to: {dashboard_path}")
    print()
    print("Run: python -m http.server 8080 --directory dashboard/")
    print("Then open: http://localhost:8080")


if __name__ == "__main__":
    main()
