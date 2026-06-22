"""Mock adapters — return synthetic data without real API keys."""

from __future__ import annotations

import random
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone


@dataclass
class MockPR:
    number: int
    title: str
    author: str
    state: str  # "open" | "closed" | "merged"
    created_at: str
    url: str


@dataclass
class MockIssue:
    number: int
    title: str
    author: str
    state: str
    labels: list[str]
    created_at: str


@dataclass
class MockEvent:
    title: str
    start: str
    end: str
    attendees: list[str]


@dataclass
class MockTicket:
    id: str
    title: str
    state: str  # "backlog" | "in_progress" | "done" | "blocked"
    assignee: str | None
    priority: int  # 1-4


class MockGitHubAdapter:
    """Returns synthetic PR and issue data."""

    def __init__(self, failure_rate: float = 0.0) -> None:
        self.failure_rate = failure_rate
        self.name = "github"

    def fetch_prs(self) -> list[MockPR]:
        if random.random() < self.failure_rate:
            raise ConnectionError("Mock GitHub API timeout")
        return [
            MockPR(42, "Fix circuit breaker recovery race", "codex", "open", "2026-06-02T14:00:00Z", "https://github.com/hummbl-dev/founder-mode/pull/42"),
            MockPR(41, "Add kill switch CLI commands", "claude-code", "open", "2026-06-01T10:30:00Z", "https://github.com/hummbl-dev/founder-mode/pull/41"),
            MockPR(40, "Update cost tracker for new OpenAI pricing", "gemini", "merged", "2026-05-28T09:15:00Z", "https://github.com/hummbl-dev/founder-mode/pull/40"),
        ]

    def fetch_issues(self) -> list[MockIssue]:
        if random.random() < self.failure_rate:
            raise ConnectionError("Mock GitHub API timeout")
        return [
            MockIssue(101, "Flaky test in coordination bus", "claude-code", "open", ["bug", "tests"], "2026-06-01T08:00:00Z"),
            MockIssue(102, "Document delegation token format", "gemini", "open", ["docs"], "2026-05-30T16:00:00Z"),
            MockIssue(100, "Upgrade Python to 3.14", "codex", "closed", ["chore"], "2026-05-20T11:00:00Z"),
        ]

    def health_check(self) -> dict:
        time.sleep(0.01)
        return {"status": "healthy", "latency_ms": 12}


class MockCalendarAdapter:
    """Returns synthetic calendar events."""

    def __init__(self, failure_rate: float = 0.0) -> None:
        self.failure_rate = failure_rate
        self.name = "calendar"

    def fetch_events(self) -> list[MockEvent]:
        if random.random() < self.failure_rate:
            raise ConnectionError("Mock Calendar API timeout")
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        return [
            MockEvent("Standup", f"{today}T10:00:00Z", f"{today}T10:15:00Z", ["claude-code", "codex", "gemini"]),
            MockEvent("Architecture Review", f"{today}T14:00:00Z", f"{today}T15:00:00Z", ["claude-code", "operator"]),
            MockEvent("1:1 with Dan", f"{today}T16:00:00Z", f"{today}T16:30:00Z", ["sov", "operator"]),
        ]

    def health_check(self) -> dict:
        time.sleep(0.01)
        return {"status": "healthy", "latency_ms": 8}


class MockLinearAdapter:
    """Returns synthetic Linear tickets."""

    def __init__(self, failure_rate: float = 0.0) -> None:
        self.failure_rate = failure_rate
        self.name = "linear"

    def fetch_tickets(self) -> list[MockTicket]:
        if random.random() < self.failure_rate:
            raise ConnectionError("Mock Linear API timeout")
        return [
            MockTicket("HUM-301", "Implement audit log rotation", "in_progress", "claude-code", 2),
            MockTicket("HUM-302", "Fix flaky kill switch test", "in_progress", "codex", 1),
            MockTicket("HUM-300", "Release hummbl-governance v1.0.0", "done", "claude-code", 1),
            MockTicket("HUM-303", "Update guardrails for new agent", "backlog", None, 3),
            MockTicket("HUM-304", "Review cost governor thresholds", "blocked", "gemini", 2),
        ]

    def health_check(self) -> dict:
        time.sleep(0.01)
        return {"status": "healthy", "latency_ms": 15}


class MockCostTracker:
    """Returns synthetic cost data."""

    def __init__(self, failure_rate: float = 0.0) -> None:
        self.failure_rate = failure_rate
        self.name = "cost"

    def fetch_usage(self) -> dict:
        if random.random() < self.failure_rate:
            raise ConnectionError("Mock cost API timeout")
        return {
            "total": 12.40,
            "budget": 50.00,
            "providers": {
                "anthropic": 8.50,
                "openai": 3.20,
                "ollama": 0.70,
            },
        }

    def health_check(self) -> dict:
        time.sleep(0.01)
        return {"status": "healthy", "latency_ms": 5}
