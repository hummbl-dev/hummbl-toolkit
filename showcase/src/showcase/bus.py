"""In-memory TSV coordination bus — single-process, no flock locking."""

from __future__ import annotations

from datetime import datetime, timezone
from io import StringIO


class InMemoryBus:
    """Append-only TSV bus for the demo.

    The real HUMMBL bus uses:
    - flock-based mutual exclusion across processes
    - TSV format with 5 columns: timestamp, from, to, type, message
    - Persistent file at founder_mode/_state/coordination/messages.tsv
    """

    def __init__(self) -> None:
        self.messages: list[dict] = []

    def post(self, from_agent: str, to_agent: str, msg_type: str, message: str) -> None:
        entry = {
            "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "from": from_agent,
            "to": to_agent,
            "type": msg_type,
            "message": message,
        }
        self.messages.append(entry)

    def tail(self, n: int = 10) -> list[dict]:
        return self.messages[-n:]

    def to_tsv(self) -> str:
        out = StringIO()
        out.write("timestamp\tfrom\tto\ttype\tmessage\n")
        for m in self.messages:
            out.write(f"{m['timestamp']}\t{m['from']}\t{m['to']}\t{m['type']}\t{m['message']}\n")
        return out.getvalue()

    def __len__(self) -> int:
        return len(self.messages)
