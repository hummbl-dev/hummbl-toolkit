# AGENTS.md — bif

## Project

**bif** — Batch Ingestion Framework: a systematic methodology for technical knowledge acquisition using AI assistants. Structured consumption in priority order (4 phases, 10+ batches) with per-batch checklists, domain templates, and a stdio MCP server. Python 3.11+, stdlib-only.

## Scope

- In scope: BIF methodology (`FRAMEWORK.md`), domain-specific starter templates (`templates/` — AI/ML platform, cloud platform, SaaS evaluation, programming framework), proven ingestion examples (`examples/` — Anthropic ecosystem), stdio MCP server (`mcp_server.py`), CLI (`bif_cli.py`), session management
- Out of scope: Consumer app features, governance primitives, bus protocol

## Setup

```bash
git clone https://github.com/hummbl-dev/bif.git && cd bif
python -m venv .venv && source .venv/bin/activate
pip install -e ".[test]"
```

MCP server startup:

```bash
python mcp_server.py
```

Optional env: `BIF_SESSIONS_DIR` overrides default temp-directory session store.

## Testing

```bash
python -m pytest tests/ -v
```

Test extras: `pytest>=9.1.0`. Test paths: `tests/`, files matching `test_*.py`.

## Conventions

- Python 3.11+ required
- Zero runtime dependencies (stdlib only)
- MCP server exposes framework as tools for MCP-compatible clients
- Sessions default to OS temp dir under `bif-sessions/` unless `BIF_SESSIONS_DIR` is set
- Commit format: Conventional Commits
- Branch naming: `type/agent/short-desc`
- Apache 2.0 license

## CI

GitHub Actions present (`.github/workflows/`). No Gitea mirror.
