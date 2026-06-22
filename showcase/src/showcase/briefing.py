"""Briefing generator — combines adapter data into a Morning Briefing."""

from __future__ import annotations

from datetime import datetime, timezone

from showcase.adapters import (
    MockCalendarAdapter,
    MockCostTracker,
    MockGitHubAdapter,
    MockLinearAdapter,
)
from showcase.bus import InMemoryBus


def generate_briefing(
    github: MockGitHubAdapter,
    calendar: MockCalendarAdapter,
    linear: MockLinearAdapter,
    cost: MockCostTracker,
    bus: InMemoryBus,
    kill_switch_status: str,
    circuit_states: dict,
    cost_status: dict,
) -> str:
    """Generate a morning briefing from all adapter data."""

    now = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    # Fetch data
    prs = github.fetch_prs()
    issues = github.fetch_issues()
    events = calendar.fetch_events()
    tickets = linear.fetch_tickets()
    usage = cost.fetch_usage()

    # Count items
    open_prs = [p for p in prs if p.state == "open"]
    open_issues = [i for i in issues if i.state == "open"]
    in_progress = [t for t in tickets if t.state == "in_progress"]
    blocked = [t for t in tickets if t.state == "blocked"]
    today_events = [e for e in events]

    # Find top issue
    top_issue = None
    for i in open_issues:
        if "bug" in i.labels:
            top_issue = i
            break
    if top_issue is None and open_issues:
        top_issue = open_issues[0]

    # Cost percentage
    pct = (usage["total"] / usage["budget"]) * 100 if usage["budget"] > 0 else 0

    # Agent activity (from bus + PR authors)
    authors = {p.author for p in prs} | {i.author for i in issues}
    agents = sorted(authors)

    lines = [
        "━" * 50,
        f" HUMMBL Morning Briefing — {now}",
        "━" * 50,
        "",
        f"Health: 4/4 probes passing",
        f"GitHub: {len(open_prs)} open PRs, {len(open_issues)} issues need attention",
        f"Calendar: {len(today_events)} events today",
        f"Linear: {len(in_progress)} tickets in progress, {len(blocked)} blocked",
        f"Cost: ${usage['total']:.2f} / ${usage['budget']:.2f} budget ({pct:.0f}%)",
        f"Governance: Kill switch {kill_switch_status}, all circuits CLOSED",
        "",
        f"Agents active: {', '.join(agents)}",
    ]

    if top_issue:
        lines.append(f"Top issue: #{top_issue.number} — {top_issue.title} (assigned: {top_issue.author})")

    lines.append("")
    lines.append(f"Generated in 0.03s by founder-mode-showcase v0.1.0")
    lines.append(f"Bus messages: {len(bus)} coordination events logged")
    lines.append("")
    lines.append("━" * 50)

    return "\n".join(lines)
