# Traffic Management — deploy-cloudrun

## Revision Naming

Cloud Run revisions follow the pattern: `<service>-<suffix>`

- Suffix is auto-generated as `YYYYMMDD-HHMMSS` (UTC) if not specified
- Custom suffixes must match: `^[a-z][a-z0-9-]{0,95}$`

## Traffic Split Format

Traffic splits are specified as comma-separated `revision=percentage` pairs:

```
my-service-20260227-120000=80,my-service-20260226-100000=20
```

Rules:
- Percentages must be integers 0-100
- All percentages must sum to exactly 100
- Each revision must exist and be in a ready state

## Deployment Patterns

### Direct Cutover (Default)

New revision receives 100% traffic immediately after deployment:

```
traffic.py --service my-svc --project my-proj --region us-central1 \
  --revisions "my-svc-20260227-120000=100"
```

### Canary Deployment

Route a small percentage of traffic to the new revision:

```
# Step 1: Deploy new revision (gets 0% traffic by default if --no-traffic)
deploy.py --service my-svc --project my-proj --region us-central1 \
  --image gcr.io/my-proj/my-svc:v2 --environment staging

# Step 2: Route 10% traffic to new revision
traffic.py --service my-svc --project my-proj --region us-central1 \
  --revisions "my-svc-20260227-120000=10,my-svc-20260226-100000=90"

# Step 3: Monitor, then promote to 100%
traffic.py --service my-svc --project my-proj --region us-central1 \
  --revisions "my-svc-20260227-120000=100"
```

### Rollback via Traffic

Route 100% traffic back to the previous revision:

```
rollback.py --service my-svc --project my-proj --region us-central1 \
  --revision my-svc-20260226-100000 --reason "latency regression"
```

## Traffic Update Behavior

- Traffic updates are atomic — all revision percentages are set in a single API call
- Revisions not listed in the split receive 0% traffic
- Traffic updates propagate within seconds
- The `traffic.py` script validates the split before applying

## Monitoring After Traffic Changes

After any traffic change, use `status.py` to verify:

```
status.py --service my-svc --project my-proj --region us-central1
```

This reports:
- Active revision(s) and their traffic percentages
- Health status of each revision receiving traffic
- Service URL
