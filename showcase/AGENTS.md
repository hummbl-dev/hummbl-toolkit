# AGENTS.md — founder-mode-showcase

## Project
**founder-mode-showcase** — Demo the HUMMBL multi-agent governance mesh in 5 minutes — zero API keys, zero config. Python 3.11+, Apache 2.0.

## Scope
- In scope: A self-contained demo that simulates a HUMMBL "Morning Briefing" using mock adapters (GitHub, Calendar, Linear, Cost) and real governance primitives (KillSwitch, CircuitBreaker, CostGovernor, HealthProbe). Produces a markdown briefing and a static HTML dashboard.
- Out of scope: Real API integrations, production deployment, persistent state, the full founder-mode runtime.

## Setup
```bash
# Option A: uv (recommended)
uv venv && source .venv/bin/activate
uv pip install -e .

# Option B: pip
python -m venv .venv && source .venv/bin/activate
pip install -e .
```
No env vars, tokens, or API keys required — all data is mocked.

## Testing
```bash
pytest
```
Dev dependencies include pytest>=7.0. The demo itself runs via `python showcase.py`. View the dashboard with `python -m http.server 8080 --directory dashboard/`.

## Conventions
- Python 3.11+; stdlib-first with `hummbl-governance` as the only runtime dependency
- Commit format: Conventional Commits (`feat:`, `fix:`, `docs:`, etc.)
- Branch naming: `type/agent/short-desc`
- Docker support via `Dockerfile` and `docker-compose.yml`

## CI
No GitHub Actions workflows currently configured. Validation is manual via `python showcase.py` and `pytest`.
