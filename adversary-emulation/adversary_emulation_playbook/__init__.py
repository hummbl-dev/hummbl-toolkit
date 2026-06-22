"""Adversary Emulation Playbook — governed MITRE ATT&CK emulation.

A Tier-1 HUMMBL primitive demonstrating how governance infrastructure
(kill switch, audit log, delegation tokens) applies to red team operations.

Every emulation step is logged, scoped, and halt-able.
"""

__version__ = "0.1.0"

from .emulate import EmulationEngine
from .playbook_loader import PlaybookLoader
from .gap_analyzer import GapAnalyzer

__all__ = ["EmulationEngine", "PlaybookLoader", "GapAnalyzer"]
