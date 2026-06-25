# AGENTS.md - hummbl-toolkit

Cross-agent instructions for AI coding agents working in this repository.

## Project

hummbl-toolkit - HUMMBL supplementary tooling — evidence-gate, batch ingestion, showcase, adversary emulation

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[test]"
```

## Conventions

- Python 3.11+ required
- Zero third-party runtime dependencies (stdlib only)
- Conventional Commits format
- No secrets in code - all credentials via environment variables

## Session rules

1. Do not revert unrelated local changes
2. Follow existing code patterns
3. Run tests after significant changes
4. Never hardcode secrets or tokens

## Branch policy

- Branch naming: `type/agent/short-desc`
- Squash-merge to main
- CI must be green before merge
