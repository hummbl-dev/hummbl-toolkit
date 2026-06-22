# Adversary Emulation Playbook

[![Tier: 1](https://img.shields.io/badge/Tier-1-stdlib--only-blue)](https://github.com/hummbl-dev/hummbl-dev)
[![HUMMBL Governance](https://img.shields.io/badge/HUMMBL-Governance-green)](https://pypi.org/project/hummbl-governance/)
[![MITRE ATT&CK](https://img.shields.io/badge/MITRE-ATT%26CK-red)](https://attack.mitre.org/)
[![Tests](https://img.shields.io/badge/tests-91%25-green)](https://github.com/hummbl-dev/adversary-emulation-playbook/actions)

> **Governed adversary emulation** — MITRE ATT&CK playbooks executed with HUMMBL governance primitives: append-only audit logs, delegation-scoped tokens, and emergency kill switches.
>
> This is not a red team toolkit. It is a **proof that safety infrastructure and offensive research can coexist** — every emulation step is logged, scoped, and halt-able.

---

## What This Repo Demonstrates

| Hiring Signal | This Repo Target | Evidence |
|---|---|---|
| Adversary emulation plans | **Yes** — MITRE ATT&CK mapped playbooks for APT28, Lazarus | `scenarios/` directory |
| Governance integration | **Yes** — Every step uses `audit_log`, `delegation_token`, `kill_switch` | `adversary_emulation_playbook/audit.py` |
| Detection gap analysis | **Yes** — Produces defender-facing gap reports with Base120 transforms | `gap_analyzer.py` |
| Conference talk material | **Target** — "Governed Adversary Emulation: Audit Trails for Red Teams" | Blog post / talk proposal |

**Unique differentiator:** No other open-source adversary emulation framework combines MITRE ATT&CK playbooks with append-only governance audit trails. This is a genuinely novel intersection.

---

## Quick Start

```bash
pip install -e ".[dev]"

# List available playbooks
aep-emulate list

# Validate a playbook (safety check)
aep-emulate validate apt28

# Run emulation with no detection rules (expect all missed)
aep-emulate run apt28 --output report.json

# Run emulation with detection rules (expect some detected)
aep-emulate run apt28 \
  --detection-rules examples/apt28_detections.json \
  --gap-analysis \
  --output report_with_gaps.json
```

---

## Architecture

```
adversary_emulation_playbook/
├── emulate.py          # Core engine — runs playbooks with governance
├── audit.py            # HUMMBL primitive wrappers (audit_log, delegation, kill_switch)
├── playbook_loader.py  # YAML/JSON playbook parser (stdlib-only)
├── gap_analyzer.py     # Detection coverage analysis with Base120 transforms
├── cli.py              # Command-line interface
└── scenarios/
    ├── apt28.yaml      # APT28 (Fancy Bear) initial access + persistence
    └── lazarus.yaml    # Lazarus Group spear-phishing + exfiltration
```

See [ARCHITECTURE.md](ARCHITECTURE.md) for full design rationale.

---

## Governance Integration

Every emulation is wrapped by three HUMMBL primitives:

1. **`audit_log`** — Every step produces an `EmulationReceipt` with SHA-256 content integrity. Receipts are appended to an immutable JSONL audit trail.
2. **`delegation_token`** — Each emulation run is scoped by a time-limited, chain-depth-limited token. Tokens are revoked on completion.
3. **`kill_switch`** — If emulation targets non-lab hosts, the kill switch engages `EMERGENCY` and aborts immediately. Real execution is intentionally unsupported.

```python
from adversary_emulation_playbook.emulate import EmulationEngine

engine = EmulationEngine()
report = engine.run("apt28", detection_rules={"T1566.001": ["sigma_phishing"]})
# report.receipts contains immutable audit trail
# report.coverage shows detection coverage fraction
```

---

## Dependency Tier

| Layer | Tier | Policy |
|---|---|---|
| Core (`emulate.py`, `audit.py`, `playbook_loader.py`) | **Tier 1** | stdlib-only + `hummbl-governance` (Tier 1) |
| CLI (`cli.py`) | **Tier 1** | stdlib-only |
| Visualization (`[visualize]` extra) | **Tier 3** | `matplotlib` optional |

Run `dep-check` in CI enforces zero third-party runtime dependencies in core.

---

## MITRE ATT&CK Mapping

| Playbook | Tactics | Techniques |
|---|---|---|
| **APT28** | Initial Access, Persistence, Execution, Privilege Escalation | T1566.001, T1053.005, T1059.001, T1078 |
| **Lazarus** | Initial Access, Execution, Exfiltration | T1566.002, T1059.003, T1020 |

Each playbook includes:
- Expected detection rules (Sigma IDs)
- Lab-only safety flag
- Target host constraints
- Base120 transform recommendations for gap analysis

---

## Gap Analysis Example

```json
{
  "gap_analysis": {
    "coverage_score": 0.25,
    "risk_score": 0.875,
    "total_gaps": 3,
    "critical_gaps": 2,
    "gaps": [
      {
        "technique_id": "T1566.001",
        "technique_name": "Spearphishing Attachment",
        "tactic": "initial-access",
        "gap_type": "missing_rule",
        "severity": "critical",
        "recommendation": "Deploy detection rules for T1566.001: sigma_phishing_attachment_exec, sigma_office_macro_suspicious",
        "base120_transform": "P"
      }
    ]
  }
}
```

---

## Safety Guarantees

- **Lab-only by default:** Every step in every playbook has `lab_only: true`. Targeting non-local hosts engages the kill switch.
- **Simulation only:** `simulate=True` is enforced. Real exploit execution is not implemented and will raise `EmulationHalted`.
- **Immutable audit trail:** Every receipt has a SHA-256 content hash. Tampering is detectable.
- **Defensive mitigations included:** Every gap analysis produces defender-facing recommendations.

---

## Hiring Signal Roadmap

| Timeline | Deliverable | Signal |
|---|---|---|
| Month 1 | Repo shipped with 2 playbooks, CI, governance integration | GitHub proof-of-work |
| Month 2 | Blog post: "Governed Adversary Emulation with HUMMBL" | Published research |
| Month 3 | Add 3 more APT playbooks + detection rule library | Expanded portfolio |
| Month 4 | Submit talk to BSides / regional conference | Conference credibility |
| Month 6 | First CVE in cryptographic implementation (crypto-sandbox) | CVE weighting (3-5x) |

---

## License

Apache-2.0. See [LICENSE](LICENSE).

---

*Generated with HUMMBL governance primitives. Every significant action is logged to the coordination bus.*
