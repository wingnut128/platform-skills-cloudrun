# deploy-cloudrun

A Claude AI skill for deploying and managing Google Cloud Run services with input validation, traffic management, rollback, and audit logging.

## Structure

```
platform-skills-cloudrun/
├── SKILL.md                    # Main Claude instruction file
├── CLAUDE.md                   # Project guidance for Claude Code
├── references/
│   ├── error-codes.md          # E0XX–E7XX error code reference
│   ├── rollback-policy.md      # Rollback mechanism and safety checks
│   ├── traffic-management.md   # Canary, cutover, rollback patterns
│   └── auth-model.md           # ServiceNow change ID authorization
├── scripts/
│   ├── deploy.py               # Deploy new revision
│   ├── status.py               # Check service health
│   ├── traffic.py              # Update traffic routing
│   ├── rollback.py             # Revert to previous revision
│   ├── authorize.py            # Authorization gate (PINNED)
│   └── lib/
│       ├── validate.py         # Input validation
│       ├── output.py           # Credential sanitization
│       ├── audit_client.py     # Local JSON lines audit
│       ├── vault_client.py     # Vault client (PINNED)
│       └── cloudrun_client.py  # Cloud Run API client (PINNED)
└── audit/                      # Local audit logs (gitignored)
```

## Pinned (Stubbed) Components

The following are not yet implemented and return stub data:

- **`cloudrun_client.py`** — All Cloud Run API methods return realistic mock responses
- **`vault_client.py`** — Raises `NotImplementedError`
- **`authorize.py`** — Accepts any validly-formatted ServiceNow change ID without API verification

## Prerequisites

- Python 3.9+
- Google Cloud SDK (for actual deployments, not needed for stubs)
- Application Default Credentials configured (`gcloud auth application-default login`)

## Security Model

- Credentials never appear in script output — all stdout is sanitized
- Scripts authenticate via Application Default Credentials (ADC) or Vault
- Environment variables with secret-like keys are rejected — use Secret Manager references
- Audit logs are stored locally as JSON lines files
- `.gitignore` blocks credential files, audit logs, and environment files
