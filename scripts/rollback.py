#!/usr/bin/env python3
"""
Rollback a Cloud Run service to a previous revision.

Performs safety checks before routing traffic back to the target revision.
See references/rollback-policy.md for full policy.
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "lib"))

from validate import service_name, gcp_project, region, revision_name
from output import sanitized_print, safe_error
from audit_client import AuditClient
from cloudrun_client import CloudRunClient


def main():
    parser = argparse.ArgumentParser(
        description="Rollback a Cloud Run service to a previous revision via traffic routing"
    )
    parser.add_argument("--service", required=True, help="Cloud Run service name")
    parser.add_argument("--project", required=True, help="GCP project ID")
    parser.add_argument("--region", required=True, help="GCP region")
    parser.add_argument("--environment", default="dev", help="Environment for audit logging")
    parser.add_argument("--revision", required=True, help="Target revision to roll back to")
    parser.add_argument("--reason", required=True, help="Reason for rollback")
    args = parser.parse_args()

    try:
        svc = service_name(args.service)
        proj = gcp_project(args.project)
        rgn = region(args.region)
        rev = revision_name(args.revision)
    except ValueError as e:
        safe_error(str(e))

    audit = AuditClient(svc, args.environment if args.environment in ("dev", "staging", "production") else "dev", proj)
    client = CloudRunClient(proj, rgn)

    # Safety check 1: target revision exists
    revisions = client.get_revisions(svc)
    revision_names = [r["name"] for r in revisions]
    if rev not in revision_names:
        audit.write("rollback", {
            "status": "safety_check_failed",
            "reason": "target revision not found",
            "target_revision": rev,
        })
        safe_error(f"E600: Rollback target revision not found in service revision list")

    # Safety check 2: target revision is healthy
    health = client.check_health(svc)
    if not health["healthy"]:
        audit.write("rollback", {
            "status": "safety_check_failed",
            "reason": "target revision unhealthy",
            "target_revision": rev,
        })
        safe_error(f"E601: Rollback target revision is unhealthy")

    # Get current status for audit
    current_status = client.get_service_status(svc)

    # Execute rollback: route 100% traffic to target revision
    result = client.update_traffic(svc, [{"revision": rev, "percent": 100}])

    audit.write("rollback", {
        "status": "rolled_back",
        "target_revision": rev,
        "previous_revision": current_status["active_revision"],
        "reason": args.reason,
    })

    sanitized_print(f"ROLLED_BACK_TO={rev}")
    sanitized_print(f"PREVIOUS_REVISION={current_status['active_revision']}")
    sanitized_print(f"REASON={args.reason}")
    sanitized_print(f"SERVICE={svc}")
    sanitized_print(f"PROJECT={proj}")
    sanitized_print(f"REGION={rgn}")
    sanitized_print(f"STATUS=rolled_back")


if __name__ == "__main__":
    main()
