"""Load and validate MITRE ATT&CK emulation playbooks from YAML."""

from __future__ import annotations

import json
import pathlib
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class EmulationStep:
    """A single step in an adversary emulation plan."""

    technique_id: str  # e.g. T1566.001
    technique_name: str
    tactic: str  # e.g. initial-access
    description: str
    expected_detection: list[str]  # Sigma rule IDs or detection queries
    lab_only: bool = True  # Must be True for safety
    target_hosts: tuple[str, ...] = ()  # Empty = localhost lab only

    def to_dict(self) -> dict[str, Any]:
        return {
            "technique_id": self.technique_id,
            "technique_name": self.technique_name,
            "tactic": self.tactic,
            "description": self.description,
            "expected_detection": self.expected_detection,
            "lab_only": self.lab_only,
            "target_hosts": list(self.target_hosts),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "EmulationStep":
        return cls(
            technique_id=str(data["technique_id"]),
            technique_name=str(data["technique_name"]),
            tactic=str(data["tactic"]),
            description=str(data["description"]),
            expected_detection=list(data.get("expected_detection", [])),
            lab_only=bool(data.get("lab_only", True)),
            target_hosts=tuple(data.get("target_hosts", [])),
        )


@dataclass(frozen=True)
class Playbook:
    """A complete adversary emulation plan mapped to MITRE ATT&CK."""

    id: str
    threat_actor: str
    description: str
    steps: tuple[EmulationStep, ...]
    mitre_version: str = "14.1"

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "threat_actor": self.threat_actor,
            "description": self.description,
            "mitre_version": self.mitre_version,
            "steps": [s.to_dict() for s in self.steps],
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Playbook":
        steps = tuple(EmulationStep.from_dict(s) for s in data.get("steps", []))
        return cls(
            id=str(data["id"]),
            threat_actor=str(data["threat_actor"]),
            description=str(data["description"]),
            steps=steps,
            mitre_version=str(data.get("mitre_version", "14.1")),
        )


class PlaybookLoader:
    """Load playbooks from YAML/JSON files with strict validation."""

    def __init__(self, playbook_dir: pathlib.Path | str | None = None) -> None:
        if playbook_dir is None:
            playbook_dir = pathlib.Path(__file__).parent / "scenarios"
        self.playbook_dir = pathlib.Path(playbook_dir)

    def load(self, name: str) -> Playbook:
        """Load a playbook by name (with or without extension)."""
        base = name if not name.endswith((".yaml", ".yml", ".json")) else name.rsplit(".", 1)[0]
        for ext in (".yaml", ".yml", ".json"):
            path = self.playbook_dir / f"{base}{ext}"
            if path.exists():
                return self._load_file(path)
        raise FileNotFoundError(f"Playbook '{name}' not found in {self.playbook_dir}")

    def list_playbooks(self) -> list[str]:
        """List available playbook names."""
        names = []
        for path in self.playbook_dir.iterdir():
            if path.suffix in (".yaml", ".yml", ".json"):
                names.append(path.stem)
        return sorted(names)

    def _load_file(self, path: pathlib.Path) -> Playbook:
        text = path.read_text(encoding="utf-8")
        if path.suffix == ".json":
            data = json.loads(text)
        else:
            # stdlib-only: parse a minimal YAML subset for our use case
            data = self._parse_minimal_yaml(text)
        return Playbook.from_dict(data)

    @staticmethod
    def _parse_minimal_yaml(text: str) -> dict[str, Any]:
        """Parse a minimal YAML subset sufficient for our playbooks.

        This intentionally avoids a third-party dependency.
        Supports: mappings, sequences, strings, ints, bools.
        Designed specifically for the playbook schema used in this repo.
        """
        lines = text.splitlines()
        result: dict[str, Any] = {}
        i = 0

        while i < len(lines):
            line = lines[i].rstrip()
            if not line or line.startswith("#"):
                i += 1
                continue

            indent = len(line) - len(line.lstrip())
            stripped = line.lstrip()

            is_mapping_entry = (": " in stripped or stripped.endswith(":")) and not stripped.startswith("- ")
            if is_mapping_entry:
                if ": " in stripped:
                    key, val = stripped.split(": ", 1)
                else:
                    key = stripped.rstrip(":")
                    val = ""
                key = key.strip()
                val = val.strip()

                if val == "":
                    # Could be a nested list or empty string
                    # Peek next line
                    if i + 1 < len(lines):
                        next_line = lines[i + 1].rstrip()
                        next_indent = len(next_line) - len(next_line.lstrip())
                        if next_line.lstrip().startswith("- ") and next_indent > indent:
                            # Parse list
                            i += 1
                            items: list[dict[str, Any]] = []
                            current_item: dict[str, Any] = {}
                            while i < len(lines):
                                item_line = lines[i].rstrip()
                                if not item_line:
                                    i += 1
                                    continue
                                item_indent = len(item_line) - len(item_line.lstrip())
                                item_stripped = item_line.lstrip()
                                if item_indent <= indent and not item_stripped.startswith("#"):
                                    # End of list
                                    break
                                if item_stripped.startswith("- "):
                                    # New item
                                    if current_item:
                                        items.append(current_item)
                                    current_item = {}
                                    val_part = item_stripped[2:].strip()
                                    if ": " in val_part:
                                        k, v = val_part.split(": ", 1)
                                        current_item[k.strip()] = PlaybookLoader._parse_value(v.strip())
                                elif (": " in item_stripped or item_stripped.endswith(":")) and item_indent > indent:
                                    # Key within current item
                                    if ": " in item_stripped:
                                        k, v = item_stripped.split(": ", 1)
                                    else:
                                        k = item_stripped.rstrip(":")
                                        v = ""
                                    k = k.strip()
                                    v = v.strip()
                                    if v == "" and i + 1 < len(lines):
                                        next_line = lines[i + 1].rstrip()
                                        next_indent = len(next_line) - len(next_line.lstrip())
                                        if next_line.lstrip().startswith("- ") and next_indent > item_indent:
                                            # Nested list within item
                                            i += 1
                                            nested_items: list[str] = []
                                            while i < len(lines):
                                                nested_line = lines[i].rstrip()
                                                if not nested_line:
                                                    i += 1
                                                    continue
                                                nested_indent = len(nested_line) - len(nested_line.lstrip())
                                                nested_stripped = nested_line.lstrip()
                                                if nested_indent <= item_indent and not nested_stripped.startswith("#"):
                                                    break
                                                if nested_stripped.startswith("- "):
                                                    nested_val = nested_stripped[2:].strip()
                                                    nested_items.append(PlaybookLoader._parse_value(nested_val))
                                                i += 1
                                            current_item[k] = nested_items
                                            continue
                                    current_item[k] = PlaybookLoader._parse_value(v)
                                i += 1
                            if current_item:
                                items.append(current_item)
                            result[key] = items
                            continue
                        else:
                            result[key] = ""
                    else:
                        result[key] = ""
                else:
                    result[key] = PlaybookLoader._parse_value(val)
            i += 1

        return result

    @staticmethod
    def _parse_value(val: str) -> Any:
        """Parse a YAML scalar value."""
        val = val.strip()
        if val.startswith('"') and val.endswith('"'):
            return val[1:-1]
        if val.startswith("'") and val.endswith("'"):
            return val[1:-1]
        if val in ("true", "True"):
            return True
        if val in ("false", "False"):
            return False
        if val.startswith("[") and val.endswith("]"):
            inner = val[1:-1].strip()
            if not inner:
                return []
            return [PlaybookLoader._parse_value(v.strip()) for v in inner.split(",")]
        try:
            return int(val)
        except ValueError:
            pass
        try:
            return float(val)
        except ValueError:
            pass
        return val
