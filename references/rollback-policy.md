# Rollback Policy — deploy-cloudrun

## Default Behavior

Rollback mode defaults to **manual**. The operator must explicitly invoke `rollback.py` to revert.

## Mechanism

Rollback is performed via **traffic routing**, not by deleting revisions:

1. Identify the target revision (previous stable revision)
2. Route 100% traffic to the target revision
3. The failed revision remains deployed but receives 0% traffic

This approach is safe because:
- No data is lost — the failed revision can be inspected
- Rollback is instant — traffic routing updates propagate in seconds
- The operation is reversible — traffic can be re-routed again

## Safety Checks

Before executing a rollback, two checks must pass:

1. **Target revision exists** — the revision must still be present in the service's revision list
2. **Target revision is healthy** — the revision must pass a health check before receiving traffic

If either check fails, rollback is blocked and the operator is informed.

## Post-Rollback Health Check

After traffic is routed to the rollback target:

1. Wait 10 seconds for traffic to stabilize
2. Hit the health endpoint on the target revision
3. Report the health status to the operator

If the post-rollback health check fails, the operator is alerted but traffic remains on the rollback target (since the original revision was already failing).

## Rollback Scope

- Rollback affects a single Cloud Run service in a single project/region
- Rollback does not modify environment variables, secrets, or other configuration
- Rollback does not delete any revisions

## Audit

All rollback operations are logged to the audit trail with:
- Reason for rollback (operator-provided)
- Source revision (the one being rolled back from)
- Target revision (the one being rolled back to)
- Safety check results
- Post-rollback health check result
