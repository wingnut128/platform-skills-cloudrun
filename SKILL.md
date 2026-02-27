---
name: deploy-cloudrun
description: |
  Deploy a service to Google Cloud Run with traffic management and rollback.
  Trigger phrases: "deploy to cloud run", "cloud run deployment", "deploy cloudrun service",
  "update cloud run traffic", "rollback cloud run"
---

# deploy-cloudrun

Deploy and manage Google Cloud Run services with input validation, traffic management, and audit logging.

## Reference Files

| File | Purpose |
|------|---------|
| `references/error-codes.md` | All error codes (E0XX–E7XX) |
| `references/rollback-policy.md` | Rollback mechanism, safety checks, defaults |
| `references/traffic-management.md` | Canary, cutover, rollback traffic patterns |
| `references/auth-model.md` | ServiceNow change IDs, environment-based auth |

## Inputs

| Input | Required | Description |
|-------|----------|-------------|
| `service` | Yes | Cloud Run service name |
| `project` | Yes | GCP project ID |
| `region` | Yes | GCP region (from allowlist) |
| `image` | Yes (deploy) | Container image URI (tag or sha256 digest) |
| `environment` | Yes | `dev`, `staging`, or `production` |
| `change_id` | Prod only | ServiceNow change ID (`CHG` + 7-15 digits) |
| `dry_run` | No | Validate without deploying (default: false) |
| `memory` | No | Memory allocation (default: `256Mi`) |
| `cpu` | No | CPU allocation (default: `1`) |
| `concurrency` | No | Max concurrent requests (default: `80`) |
| `min_instances` | No | Minimum instances (default: `0`) |
| `max_instances` | No | Maximum instances (default: `100`) |
| `env_vars` | No | `KEY=VALUE` pairs, comma-separated |
| `service_account` | No | GCP service account email |
| `vpc_connector` | No | VPC connector resource path |
| `ingress` | No | `all`, `internal`, or `internal-and-cloud-load-balancing` |

## Procedure

### Step 1: Collect Inputs

Gather the required inputs from the operator. At minimum: service, project, region, image, environment.

For production deployments, require a `change_id`.

### Step 2: Authorize

Run authorization check. Production requires an approved ServiceNow change ID.

```bash
python3 scripts/authorize.py \
  --service <service> \
  --project <project> \
  --environment <environment> \
  --change-id <change_id>
```

**If `STATUS=denied`**: Stop. Inform the operator of the denial reason.

### Step 3: Dry Run (Optional)

Validate all inputs without deploying:

```bash
python3 scripts/deploy.py \
  --service <service> \
  --project <project> \
  --region <region> \
  --image <image> \
  --environment <environment> \
  --dry-run
```

Review the output with the operator before proceeding.

### Step 4: Deploy

Deploy the new revision:

```bash
python3 scripts/deploy.py \
  --service <service> \
  --project <project> \
  --region <region> \
  --image <image> \
  --environment <environment> \
  --change-id <change_id> \
  --memory <memory> \
  --cpu <cpu> \
  --concurrency <concurrency> \
  --min-instances <min_instances> \
  --max-instances <max_instances> \
  --env-vars <env_vars> \
  --service-account <service_account> \
  --vpc-connector <vpc_connector> \
  --ingress <ingress>
```

Capture the `REVISION` from the output.

### Step 5: Verify

Check the health of the deployed revision:

```bash
python3 scripts/status.py \
  --service <service> \
  --project <project> \
  --region <region>
```

**If `STATUS=unhealthy`**: Ask the operator whether to rollback or investigate.

### Step 6: Traffic Management (Optional)

For canary deployments or traffic splitting:

```bash
python3 scripts/traffic.py \
  --service <service> \
  --project <project> \
  --region <region> \
  --revisions "new-revision=10,old-revision=90"
```

See `references/traffic-management.md` for canary patterns.

### Step 7: Rollback (If Needed)

If the deployment needs to be reverted:

```bash
python3 scripts/rollback.py \
  --service <service> \
  --project <project> \
  --region <region> \
  --revision <previous_revision> \
  --reason "<reason>"
```

See `references/rollback-policy.md` for safety checks and behavior.

## Constraints

- **One service per invocation** — do not batch multiple services
- **Operator declares the environment** — never infer or override
- **Production requires change_id** — warn immediately if missing
- **Rollback defaults to manual** — operator must explicitly request it
- **Never construct revision names from parts** — use full names as returned by deploy/status
- **Never read, print, or pass credential values** between steps

## Security

- All script output is sanitized via `scripts/lib/output.py`
- Credentials use ADC or Vault — never passed through Claude's context
- Environment variables with secret-like keys are rejected (E501) — use Secret Manager references
- Audit logs are written locally to `./audit/` as JSON lines
