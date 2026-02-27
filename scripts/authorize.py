#!/usr/bin/env python3
"""
Authorization gate for Cloud Run deployments.

PINNED — ServiceNow validation is stubbed.
Production deployments require an approved change ID.
Non-production environments bypass authorization.
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "lib"))

from validate import environment as validate_environment, change_id as validate_change_id
from output import sanitized_print, safe_error
from audit_client import AuditClient


def main():
    parser = argparse.ArgumentParser(
        description="Authorize a Cloud Run deployment via ServiceNow change ID"
    )
    parser.add_argument("--service", required=True, help="Cloud Run service name")
    parser.add_argument("--project", required=True, help="GCP project ID")
    parser.add_argument("--environment", required=True, help="Target environment (dev|staging|production)")
    parser.add_argument("--change-id", default=None, help="ServiceNow change ID (required for production)")
    args = parser.parse_args()

    try:
        env = validate_environment(args.environment)
    except ValueError as e:
        safe_error(str(e))

    audit = AuditClient(args.service, env, args.project)

    # Non-production: authorize immediately
    if env != "production":
        audit.write("authorize", {"status": "authorized", "reason": "non-production environment"})
        sanitized_print(f"STATUS=authorized")
        sanitized_print(f"ENVIRONMENT={env}")
        return

    # Production: require change_id
    if not args.change_id:
        audit.write("authorize", {"status": "denied", "reason": "missing change_id"})
        safe_error("E104: Production deployment requires a change_id")

    try:
        cid = validate_change_id(args.change_id)
    except ValueError as e:
        audit.write("authorize", {"status": "denied", "reason": str(e)})
        safe_error(str(e))

    # STUB — PINNED: would check ServiceNow API for approval status
    # For now, accept any validly-formatted change ID
    audit.write("authorize", {"status": "authorized", "change_id": cid})
    sanitized_print(f"STATUS=authorized")
    sanitized_print(f"CHANGE_ID={cid}")
    sanitized_print(f"ENVIRONMENT={env}")


if __name__ == "__main__":
    main()
