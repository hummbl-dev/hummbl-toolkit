# BIF — Batch Ingestion Framework

**A systematic methodology for technical knowledge acquisition using AI assistants.**

[![License](https://img.shields.io/badge/license-Apache%202.0-blue)](LICENSE)

---

## What is BIF?

BIF is a repeatable framework for building comprehensive knowledge bases on any company, product, service, or technical domain. Developed during CCA-F certification prep and proven across 10 batches covering the entire Anthropic ecosystem in a single session.

The core insight: **structured consumption in priority order, with each batch building on the last, creates layered understanding that random reading never achieves.**

## The Four Phases

```
Phase 1: FOUNDATION (Batches 1-4)   → What it is, how it works, what's current
Phase 2: TECHNIQUE  (Batches 5-7)   → How to use it well, how to avoid mistakes
Phase 3: SOURCE     (Batches 8-10)  → How the creators use it, what to clone
Phase 4: ECOSYSTEM  (Batches 11+)   → Adjacent tools, community, competitive context
```

## Quick Start

1. Read [FRAMEWORK.md](FRAMEWORK.md) — the complete methodology
2. Copy a [domain-specific template](templates/) for your target
3. Execute batches 1-10 using the [per-batch checklist](FRAMEWORK.md#32-per-batch-execution-checklist)
4. Upload knowledge files to your Claude Project

## Files

| File | What |
|------|------|
| [FRAMEWORK.md](FRAMEWORK.md) | Complete BIF methodology — phases, checklists, templates, hardening protocols |
| [templates/](templates/) | Domain-specific starter templates |
| [examples/](examples/) | Proven ingestion results (Anthropic ecosystem) |

## Domain Templates

| Domain | Template |
|--------|----------|
| AI/ML Platform | [ai-ml-platform.md](templates/ai-ml-platform.md) |
| Cloud Platform (AWS/GCP/Azure) | [cloud-platform.md](templates/cloud-platform.md) |
| SaaS Product Evaluation | [saas-evaluation.md](templates/saas-evaluation.md) |
| Programming Framework | [programming-framework.md](templates/programming-framework.md) |

## MCP Server

BIF includes a stdio MCP server that exposes the framework as tools for MCP-compatible clients.

### Required environment

| Variable | Required | Purpose |
|----------|----------|---------|
| `BIF_SESSIONS_DIR` | No | Overrides the default temp-directory session store. Use this when you want sessions persisted in a known workspace path. |

If `BIF_SESSIONS_DIR` is not set, sessions are written under the operating system temp directory in `bif-sessions/`.

### Startup command

```bash
python mcp_server.py
```

Example MCP client configuration:

```json
{
  "mcpServers": {
    "bif": {
      "command": "python",
      "args": ["/absolute/path/to/bif/mcp_server.py"],
      "env": {
        "BIF_SESSIONS_DIR": "/absolute/path/to/bif/.sessions"
      }
    }
  }
}
```

The server supports `initialize`, `tools/list`, `tools/call`, and `ping` over newline-delimited JSON-RPC on stdio.

## Proven Results

| Project | Batches | Files | Time | Coverage |
|---------|---------|-------|------|----------|
| Anthropic Ecosystem | 10 | 13 | ~4 hours | Comprehensive (API, MCP, Claude Code, safety, research) |

## Who is this for?

- **Developers** evaluating new platforms or preparing for certifications
- **Architects** onboarding onto unfamiliar technology stacks
- **Consultants** who need to become conversant in a client's tech quickly
- **Teams** building shared knowledge bases for AI-assisted workflows

## About

Built by [HUMMBL, LLC](https://hummbl.io) — cognitive AI architecture for production systems.

BIF applies the same structured reasoning principles as [Base120](https://github.com/hummbl-dev/base120) to the problem of knowledge acquisition: decompose the domain, compose understanding in layers, and recurse until mastery.

---

Apache 2.0. Copyright 2026 HUMMBL, LLC.
