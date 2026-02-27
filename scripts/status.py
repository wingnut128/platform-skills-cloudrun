#!/usr/bin/env python3
"""
Check the health and status of a Cloud Run service.

Reports active revision, readiness, traffic split, and health check results.
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "lib"))

from validate import service_name, gcp_project, region
from output import sanitized_print, safe_error
from audit_client import AuditClient
from cloudrun_client import CloudRunClient


def main():
    parser = argparse.ArgumentParser(
        description="Check health and status of a Cloud Run service"
    )
    parser.add_argument("--service", required=True, help="Cloud Run service name")
    parser.add_argument("--project", required=True, help="GCP project ID")
    parser.add_argument("--region", required=True, help="GCP region")
    parser.add_argument("--environment", default="dev", help="Environment for audit logging")
    parser.add_argument("--health-endpoint", default="/health", help="Health check endpoint path")
    args = parser.parse_args()

    try:
        svc = service_name(args.service)
        proj = gcp_project(args.project)
        rgn = region(args.region)
    except ValueError as e:
        safe_error(str(e))

    client = CloudRunClient(proj, rgn)
    audit = AuditClient(svc, args.environment if args.environment in ("dev", "staging", "production") else "dev", proj)

    # Get service status
    status = client.get_service_status(svc)

    # Check health
    health = client.check_health(svc, args.health_endpoint)

    overall = "healthy" if status["ready"] and health["healthy"] else "unhealthy"

    # Format traffic split
    traffic_parts = []
    for entry in status["traffic"]:
        traffic_parts.append(f"{entry['revision']}={entry['percent']}")
    traffic_str = ",".join(traffic_parts)

    audit.write("status_check", {
        "active_revision": status["active_revision"],
        "ready": status["ready"],
        "healthy": health["healthy"],
        "status": overall,
    })

    sanitized_print(f"ACTIVE_REVISION={status['active_revision']}")
    sanitized_print(f"READY={status['ready']}")
    sanitized_print(f"TRAFFIC_SPLIT={traffic_str}")
    sanitized_print(f"HEALTH_STATUS={overall}")
    sanitized_print(f"HEALTH_ENDPOINT={args.health_endpoint}")
    sanitized_print(f"LATENCY_MS={health['latency_ms']}")
    sanitized_print(f"URL={status['url']}")
    sanitized_print(f"STATUS={overall}")


if __name__ == "__main__":
    main()
