# DOCTRINE.md - hummbl-toolkit

**Status:** v0.1
**Steward:** HUMMBL Research Institute

## 1. Thesis
This repo consolidates supplementary tooling for HUMMBL governance infrastructure into a single toolkit. It preserves four previously standalone repos — evidence-gate, bif, showcase, and adversary-emulation — as subdirectories with their original content and licenses intact. The bet is that consolidation reduces discovery cost and maintenance overhead while preserving provenance.

Each subdirectory retains its original README and LICENSE, making the toolkit a federation rather than a merge. Content is preserved as-is from the archived source repos, with redirect pointers left behind.

## 2. Conceptual vocabulary
- **Evidence-gate** — pre-publish source-verification rule library using stdlib-only TOML rules.
- **BIF** — Batch Ingestion Framework for systematic technical knowledge acquisition with AI assistants.
- **Showcase** — zero-config Docker demo of the HUMMBL multi-agent governance mesh.
- **Adversary emulation** — MITRE ATT&CK emulation with HUMMBL governance audit trail.
- **Consolidation** — act of merging standalone repos into subdirectories with redirect pointers.

## 3. Design principles
1. Preserve provenance — each subdirectory retains its original README and LICENSE.
2. Content is frozen — consolidation preserves as-is, it does not refactor.
3. One repo, many tools — discovery cost drops when tooling lives in one place.
4. Redirect pointers remain — archived repos point here so links don't break.

## 4. Boundaries
- Not a unified codebase — subdirectories are independent, not integrated.
- Not a replacement for per-tool documentation — each subdirectory has its own README.
- Not a build target — no shared build system across subdirectories.
- Not a governance authority — it is a tool collection, not a governance definition.

## 5. Open questions
- Should subdirectories eventually be unified into a shared package structure?
- How to handle cross-tool dependencies that emerge after consolidation?
- When should a tool graduate from the toolkit into its own repo?
