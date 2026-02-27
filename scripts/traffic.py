#!/usr/bin/env python3
"""
Update traffic routing for a Cloud Run service.

Accepts a traffic split specification and applies it atomically.
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "lib"))

from validate import service_name, gcp_project, region, traffic_split as validate_traffic_split
from output import sanitized_print, safe_error
from audit_client import AuditClient
from cloudrun_client import CloudRunClient


def parse_split_string(split_str: str) -> list:
    """Convert 'rev1=50,rev2=50' to [{"revision": "rev1", "percent": 50}, ...]."""
    result = []
    for part in split_str.split(","):
        rev, pct = part.strip().split("=", 1)
        result.append({"revision": rev.strip(), "percent": int(pct.strip())})
    return result


def main():
    parser = argparse.ArgumentParser(
        description="Update traffic routing for a Cloud Run service"
    )
    parser.add_argument("--service", required=True, help="Cloud Run service name")
    parser.add_argument("--project", required=True, help="GCP project ID")
    parser.add_argument("--region", required=True, help="GCP region")
    parser.add_argument("--environment", default="dev", help="Environment for audit logging")
    parser.add_argument("--revisions", required=True, help="Traffic split: rev1=50,rev2=50 (must sum to 100)")
    args = parser.parse_args()

    try:
        svc = service_name(args.service)
        proj = gcp_project(args.project)
        rgn = region(args.region)
        validate_traffic_split(args.revisions)
    except ValueError as e:
        safe_error(str(e))

    splits = parse_split_string(args.revisions)

    audit = AuditClient(svc, args.environment if args.environment in ("dev", "staging", "production") else "dev", proj)
    client = CloudRunClient(proj, rgn)

    result = client.update_traffic(svc, splits)

    # Format traffic for output
    traffic_parts = []
    for entry in result["traffic"]:
        traffic_parts.append(f"{entry['revision']}={entry['percent']}")
    traffic_str = ",".join(traffic_parts)

    audit.write("traffic_update", {
        "status": result["status"],
        "traffic": traffic_str,
    })

    sanitized_print(f"TRAFFIC_SPLIT={traffic_str}")
    sanitized_print(f"SERVICE={svc}")
    sanitized_print(f"PROJECT={proj}")
    sanitized_print(f"REGION={rgn}")
    sanitized_print(f"STATUS={result['status']}")


if __name__ == "__main__":
    main()
