# CONSTITUTION.md — hummbl-toolkit

**Status:** v0.1
**Steward:** HUMMBL Research Institute
**Approving human:** Reuben Bowlby
**Standard:** HUMMBL Repo Standard v0.1

## 1. Identity
`hummbl-dev/hummbl-toolkit` — HUMMBL supplementary tooling — evidence-gate, batch ingestion, showcase, adversary emulation

## 2. Scope
This constitution operates under the HUMMBL Repo Standard.

## 3. Protected invariants
1. **Receipt integrity.** The Krineia chain is append-only and SHA-256-chained.
2. **No secrets in code.** No API keys, tokens, or credentials may be committed.
3. **Standard compliance.** This repo adheres to the HUMMBL Repo Standard v0.1.
4. **Test gate.** CI must be green before any merge to a protected branch.

## 4. Normative files
- `CONSTITUTION.md`, `KRINEIA.md`, `hummbl.repo.yaml`, `CODEOWNERS`, `AGENTS.md`

## 5. Authority
- **Steward:** HUMMBL Research Institute
- **Approving human:** Reuben Bowlby

## 6. Receipt-triggering changes
- Edits to normative files, protected invariants, releases

## 7. Amendment
Changes require: a PR, an ADR, a KRINEIA receipt, and human approval.
