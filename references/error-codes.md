# Error Codes — deploy-cloudrun

## E0XX — Input Validation

| Code | Description |
|------|-------------|
| E001 | Invalid service name format |
| E002 | Invalid GCP project ID format |
| E003 | Region not in allowlist |
| E004 | Invalid container image URI format |
| E005 | Environment not in allowlist |
| E006 | Invalid revision name format |
| E007 | Invalid service account email format |
| E008 | Invalid VPC connector format |
| E009 | Ingress setting not in allowlist |

## E1XX — Authorization

| Code | Description |
|------|-------------|
| E100 | Invalid change ID format |
| E101 | Change ID not found or not approved |
| E102 | Change ID expired |
| E103 | Authorization denied — insufficient approvals |
| E104 | Production deployment requires change_id |

## E2XX — Infrastructure

| Code | Description |
|------|-------------|
| E200 | Cloud Run API unreachable |
| E201 | Authentication failure (ADC/Vault) |
| E202 | Quota exceeded |
| E203 | Service not found in project/region |
| E204 | Image not found in registry |
| E205 | Permission denied on GCP resource |

## E3XX — Operation

| Code | Description |
|------|-------------|
| E300 | Deployment failed — revision did not become ready |
| E301 | Deployment timed out |
| E302 | Revision health check failed |
| E303 | Previous deployment still in progress |

## E4XX — Traffic Management

| Code | Description |
|------|-------------|
| E400 | Invalid traffic split format |
| E401 | Traffic percentage must be an integer |
| E402 | Traffic percentage must be 0-100 |
| E403 | Traffic percentages must sum to 100 |
| E404 | Target revision not found |
| E405 | Cannot route traffic to unhealthy revision |

## E5XX — Configuration

| Code | Description |
|------|-------------|
| E500 | Invalid environment variable format |
| E501 | Environment variable key suggests a secret — use Secret Manager |
| E502 | Invalid memory format |
| E503 | Invalid CPU format |
| E504 | Concurrency out of range |
| E505 | Instance count out of range |

## E6XX — Rollback

| Code | Description |
|------|-------------|
| E600 | Rollback target revision not found |
| E601 | Rollback target revision is unhealthy |
| E602 | No previous revision available for rollback |
| E603 | Rollback safety check failed |

## E7XX — Audit

| Code | Description |
|------|-------------|
| E700 | Audit log write failed |
| E701 | Audit directory not writable |
| E702 | Audit path validation failed |
