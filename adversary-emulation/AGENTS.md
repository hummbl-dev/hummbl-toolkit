# AGENTS.md — adversary-emulation-playbook

## Project

**adversary-emulation-playbook** — MITRE ATT&CK adversary emulation with HUMMBL governance audit trails. Every emulation step is logged, scoped, and halt-able via append-only audit logs, delegation-scoped tokens, and emergency kill switches. Python 3.11+, Tier 1 stdlib-only core + `hummbl-governance`.

## Scope

- In scope: MITRE ATT&CK-mapped playbooks (APT28, Lazarus), governance-integrated emulation engine (`emulate.py`), HUMMBL primitive wrappers (`audit.py` — audit_log, delegation_token, kill_switch), playbook loader (`playbook_loader.py` — YAML/JSON, stdlib-only), detection gap analysis with Base120 transforms (`gap_analyzer.py`), CLI (`cli.py`), scenario definitions (`scenarios/`)
- Out of scope: Real offensive execution (intentionally unsupported — kill switch engages EMERGENCY on non-lab hosts), red team toolkit operations, consumer app features

## Setup

```bash
git clone https://github.com/hummbl-dev/adversary-emulation-playbook.git && cd adversary-emulation-playbook
pip install -e ".[dev]"
```

## Testing

```bash
python -m pytest tests/ -v
```

Dev extras: `pytest>=7.0`, `pytest-cov>=4.0`, `mypy>=1.0`. Test paths: `tests/`.

## Conventions

- Python 3.11+ required
- Tier 1 (core: `emulate.py`, `audit.py`, `playbook_loader.py`): stdlib-only + `hummbl-governance` (also Tier 1)
- Tier 1 (CLI: `cli.py`): stdlib-only
- Tier 3 (visualization `[visualize]` extra): `matplotlib` optional
- `dep-check` in CI enforces zero third-party runtime dependencies in core
- Every emulation produces `EmulationReceipt` with SHA-256 content integrity; receipts appended to immutable JSONL audit trail
- Delegation tokens are time-limited and chain-depth-limited; revoked on completion
- Kill switch engages EMERGENCY and aborts if emulation targets non-lab hosts
- Commit format: Conventional Commits
- Branch naming: `type/agent/short-desc`
- Apache 2.0 license

## CI

GitHub Actions workflow: `ci.yml` (lint + test + dep-check enforcing zero third-party runtime deps in core).
