# KRINEIA.md — hummbl-toolkit
---
krineia_manifest_version: "0.1"
schema: "krineia-manifest@0.1"
repo:
  full_name: "hummbl-dev/hummbl-toolkit"
  default_branch: "main"
authority:
  steward: "HUMMBL Research Institute"
  approving_human: "Reuben Bowlby"
governance_profile:
  status: "adopted"
  krineia_required: true
  trust_root_mode: "deployment_asserted"
chains:
  primary:
    chain_id: "hummbl-toolkit-primary"
    storage: "_receipts/krineia/primary.jsonl"
    genesis_policy: "repo_bootstrap"
    hash_algorithm: "sha256"
operators:
  allowed: ["append", "project", "cut"]
  forbidden: ["update", "delete", "rewrite"]
boundaries:
  no_reward_path_self_reference: true
  external_analysis_only: true
last_reviewed: "2026-06-22"
---
