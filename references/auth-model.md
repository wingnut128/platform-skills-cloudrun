# Authorization Model — deploy-cloudrun

## Overview

Authorization gates deployment to production environments. Non-production environments (dev, staging) skip the authorization check.

## Production Deployments

Production deployments require a **ServiceNow change ID**:

- Format: `CHG` followed by 7-15 digits (e.g., `CHG0012345`)
- The change ID must be in an approved state in ServiceNow
- `authorize.py` validates the change ID before deployment proceeds

If no change ID is provided for a production deployment, the operation is blocked with error `E104`.

## Non-Production Deployments

Deployments to `dev` and `staging` environments:

- Do not require a change ID
- `authorize.py` returns `STATUS=authorized` immediately
- A warning is logged if a change ID is provided (accepted but unnecessary)

## Authorization Flow

```
Operator provides: environment, change_id (optional)
        │
        ▼
  ┌─────────────┐
  │ environment  │──── dev/staging ────▶ STATUS=authorized
  │   check      │
  └──────┬───────┘
         │
     production
         │
         ▼
  ┌─────────────┐
  │ change_id   │──── missing ────▶ E104: requires change_id
  │   present?  │
  └──────┬───────┘
         │
       present
         │
         ▼
  ┌─────────────┐
  │  validate   │──── invalid format ────▶ E100: invalid format
  │  format     │
  └──────┬───────┘
         │
       valid
         │
         ▼
  ┌─────────────┐
  │  check      │──── not approved ────▶ E103: denied
  │  ServiceNow │
  └──────┬───────┘
         │
      approved
         │
         ▼
    STATUS=authorized
```

## GCP Authentication

Scripts authenticate to GCP using **Application Default Credentials (ADC)**:

- In CI/CD: workload identity federation
- In development: `gcloud auth application-default login`
- Service account keys are **never** used or stored

Credentials never appear in script output — all stdout is sanitized via `output.py`.

## Vault Integration

When secrets are needed (e.g., notification webhooks), scripts fetch them internally via `vault_client.py`. The secret values never reach Claude's context or stdout.
