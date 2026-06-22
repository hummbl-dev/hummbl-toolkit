# Architecture — Adversary Emulation Playbook

> **Version:** 0.1.0
> **Date:** 2026-06-17
> **Author:** claude-code
> **Status:** Draft — awaiting operator review

---

## Purpose

Demonstrate that **governance infrastructure and adversarial research can coexist**. The Adversary Emulation Playbook is a Tier-1 HUMMBL primitive that uses MITRE ATT&CK playbooks to simulate attacker behavior while subjecting every action to three governance guarantees:

1. **Auditability** — every step is logged with content-addressed receipts
2. **Scopability** — every emulation runs under a time-limited delegation token
3. **Halting** — non-lab targets trigger emergency kill switch engagement

This is not a red team toolkit. It is a **governance substrate** for security research.

---

## Design Principles

### 1. stdlib-First Core (Tier 1)
The core engine uses only Python stdlib + `hummbl-governance` (which is itself stdlib-only). No third-party YAML parsers, no external exploit frameworks. This keeps the attack surface minimal and proves the engine can be audited.

### 2. Governance as Substrate
Governance is not a logging layer added after the fact. It is the **foundation** on which emulation runs:
- The engine cannot start without a delegation token
- The engine cannot proceed if the kill switch is engaged
- The engine cannot target non-lab hosts (verified before every step)

### 3. Defensive-Context Only
All emulation is simulation. Real exploit execution is intentionally unsupported. Every playbook includes:
- `lab_only: true` flag
- Expected detection rules (for gap analysis)
- Defensive mitigations in gap reports

### 4. Base120 Mental Model Integration
Every gap analysis recommendation includes a Base120 transform:
- **P** (Problem): Attack surface exposed
- **IN** (Insight): What detection logic is missing
- **CO** (Comparison): How others detect this
- **DE** (Design): What control to build
- **RE** (Recursion): Sub-techniques uncovered
- **SY** (Synthesis): Kill chain combinations

---

## Component Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    CLI (cli.py)                             │
│         aep-emulate list | validate | run                   │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│              EmulationEngine (emulate.py)                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Playbook   │  │   Auditor    │  │   Report     │      │
│  │   Loader     │  │   (audit.py) │  │   Builder    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│              EmulationAuditor (audit.py)                    │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  HUMMBL Governance Primitives                       │   │
│  │  ┌──────────┐ ┌──────────────┐ ┌──────────────┐   │   │
│  │  │ AuditLog │ │ Delegation   │ │ KillSwitch   │   │   │
│  │  │ (append) │ │ Token Manager│ │ (EMERGENCY)  │   │   │
│  │  └──────────┘ └──────────────┘ └──────────────┘   │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│              GapAnalyzer (gap_analyzer.py)                  │
│  Coverage scoring • Risk weighting • Defender summary       │
│  Base120 transform recommendations                          │
└─────────────────────────────────────────────────────────────┘
```

---

## Data Flow

### 1. Playbook Loading
```
YAML/JSON file → PlaybookLoader._parse_minimal_yaml → Playbook.from_dict →
EmulationStep objects (validated, lab_only enforced)
```

### 2. Emulation Execution
```
EmulationEngine.run(playbook_name):
  1. Load playbook
  2. auditor.begin_emulation() → issue delegation token
  3. For each step:
     a. auditor.check_safety(target_hosts) → kill switch if non-lab
     b. auditor.record_step(status="started")
     c. _simulate_technique() → determine detected/missed
     d. auditor.record_step(status="completed")
  4. auditor.end_emulation() → revoke token, export receipts
```

### 3. Gap Analysis
```
EmulationReport → GapAnalyzer.analyze() → GapReport
  - Severity mapped by tactic (initial-access = critical)
  - Base120 transform mapped by tactic (initial-access = P)
  - Risk score = weighted gap severity / max possible
```

---

## Safety Model

### Kill Switch States

| State | Trigger | Action |
|---|---|---|
| DISENGAGED | Normal operation | Emulation proceeds |
| HALT_NONCRITICAL | Minor anomaly | Pause, require operator override |
| HALT_ALL | Major anomaly | Abort current emulation |
| EMERGENCY | Non-lab target detected | Immediate abort, token revocation |

### Delegation Token Constraints

- **Scope:** Tied to single emulation run (`playbook_id`)
- **Expiry:** Default 3600 seconds
- **Chain depth:** Max 5 (prevents infinite recursion in multi-step chains)
- **Revocation:** Automatic on emulation completion or emergency halt

### Audit Receipt Integrity

Each `EmulationReceipt` computes a SHA-256 over its canonical JSON representation:
```python
content = json.dumps({
    "timestamp": timestamp,
    "emulation_id": emulation_id,
    "token_id": token_id,
    "technique_id": technique_id,
    "tactic": tactic,
    "status": status,
    "detail": detail,
}, sort_keys=True, separators=(',', ':'))
sha256 = hashlib.sha256(content.encode()).hexdigest()
```

Receipts are exported as newline-delimited JSON (JSONL) for append-only storage.

---

## Extension Points

### Adding a New Playbook
1. Create `scenarios/<actor>.yaml` following the schema in `Playbook.from_dict`
2. Ensure `lab_only: true` on every step
3. Add expected detection rules for gap analysis
4. Run `aep-emulate validate <actor>`

### Adding a New Detection Simulation Model
The `_simulate_technique` method in `EmulationEngine` uses a simple rule-matching model. Future versions could add:
- **Behavioral fidelity:** Simulate noise, evasion probability
- **Sigma rule evaluator:** Parse and evaluate actual Sigma rules against event data
- **MITRE ATT&CK Navigator export:** Generate `.json` for ATT&CK navigator coverage visualization

### Adding Visualization
Install `[visualize]` extra for matplotlib-based coverage plots:
```python
pip install -e ".[visualize]"
```

---

## Testing Strategy

| Layer | Coverage Target | Key Tests |
|---|---|---|
| PlaybookLoader | 100% | YAML parsing, JSON parsing, validation, missing files |
| EmulationAuditor | 100% | Token issuance, safety checks, kill switch, receipt integrity |
| EmulationEngine | ≥90% | Run with/without detections, halt on non-lab, receipt generation |
| GapAnalyzer | 100% | Gap creation, severity mapping, risk scoring, summaries |
| CLI | Smoke | list, validate, run commands |

CI runs on 3 OS × 3 Python versions with `--cov-fail-under=80`.

---

## Dependency Justification

| Package | Tier | Justification |
|---|---|---|
| `hummbl-governance` | Tier 1 | stdlib-only core; provides audit_log, delegation, kill_switch |
| `matplotlib` | Tier 3 | Optional `[visualize]` extra only; not in runtime core |
| `pytest` | Tier 3 | Dev dependency only |
| `mypy` | Tier 3 | Dev dependency only |

---

## Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| YAML parser too minimal for complex playbooks | Medium | Low | Only supports our subset; complex playbooks can use JSON |
| Kill switch not effective if compromised | Low | High | Kill switch is local-only; no remote override to prevent bypass |
| Playbook drift from MITRE ATT&CK updates | Medium | Medium | Version pinning (`mitre_version` field); update cadence documented |
| Misuse as actual attack framework | Low | High | Simulation-only; real execution unsupported; lab-only enforcement |

---

## Related HUMMBL Primitives

- `hummbl-governance.audit_log` — Append-only JSONL governance events
- `hummbl-governance.delegation_token` — HMAC-SHA256 scoped capability tokens
- `hummbl-governance.kill_switch` — 4-state emergency halt
- `hummbl-governance.schema_validator` — stdlib-only JSON Schema (used in crypto-sandbox)

---

*Architecture reviewed against HUMMBL Tier-1 extraction discipline. Ready for operator approval.*
