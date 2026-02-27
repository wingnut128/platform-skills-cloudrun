# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Purpose

Platform-skills-cloudrun is a Claude AI skill for deploying and managing Google Cloud Run services. It follows the platform-skills conventions (SKILL.md, references/, scripts/lib/) with a simplified execution model — direct script execution with local JSON audit logging.

## Architecture

- **SKILL.md** is the main Claude instruction file with the step-by-step deployment procedure
- **references/** contains detailed specs (auth, error codes, rollback, traffic management)
- **scripts/** contains Python CLI scripts Claude invokes; **scripts/lib/** has shared library modules
- **audit/** stores local JSON lines audit logs (gitignored)

### Execution Model

Unlike deploy-temporal-workers or deploy-spire-service, this skill does not use Temporal workflow orchestration. Scripts are invoked directly by Claude and produce sanitized key=value output on stdout.

### Key Components

| Component | Purpose |
|-----------|---------|
| `scripts/deploy.py` | Deploy new Cloud Run revision |
| `scripts/status.py` | Check service health and traffic |
| `scripts/traffic.py` | Update traffic routing between revisions |
| `scripts/rollback.py` | Revert to a previous revision via traffic routing |
| `scripts/authorize.py` | Authorization gate (ServiceNow change ID) |
| `scripts/lib/validate.py` | Input validation with allowlists and regex |
| `scripts/lib/output.py` | Credential sanitization for stdout |
| `scripts/lib/audit_client.py` | Local JSON lines audit logging |
| `scripts/lib/cloudrun_client.py` | Cloud Run API client (PINNED stub) |
| `scripts/lib/vault_client.py` | Vault secret fetcher (PINNED stub) |

## Implementation Status

Many scripts are **PINNED** (stubbed). Key items not yet implemented:
- `authorize.py` — ServiceNow API validation is stubbed (accepts any valid-format change ID)
- `cloudrun_client.py` — all Cloud Run API methods return realistic stub data
- `vault_client.py` — Vault integration raises NotImplementedError
- Health checks are simulated (always returns healthy)

## Critical Design Constraints

- **One service per invocation** — do not batch deployments
- **Environment is always declared by the operator** — Claude must never infer or override
- **Production deployments require a ServiceNow change_id** — warn if missing
- **Rollback defaults to manual** — operator must explicitly request
- **Never construct revision names from parts** — use full names as returned by scripts
- **Never read, print, or pass credential values** between steps
- **Reject secret-like keys in env_vars** (E501) — use Secret Manager references instead

## Security Scanning

When generating new Python code, run Snyk code scanning. Fix any issues found and rescan until clean.
