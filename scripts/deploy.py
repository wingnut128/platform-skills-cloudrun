#!/usr/bin/env python3
"""
Deploy a new Cloud Run revision.

Validates all inputs, optionally performs a dry run, then deploys
via the Cloud Run client. All output is sanitized.
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "lib"))

from validate import (
    service_name, gcp_project, region, image_uri, environment,
    memory as validate_memory, cpu as validate_cpu,
    concurrency as validate_concurrency, instances as validate_instances,
    env_vars as validate_env_vars, service_account as validate_sa,
    vpc_connector as validate_vpc, ingress as validate_ingress,
)
from output import sanitized_print, safe_error
from audit_client import AuditClient
from cloudrun_client import CloudRunClient


def main():
    parser = argparse.ArgumentParser(
        description="Deploy a new revision to a Cloud Run service"
    )
    parser.add_argument("--service", required=True, help="Cloud Run service name")
    parser.add_argument("--project", required=True, help="GCP project ID")
    parser.add_argument("--region", required=True, help="GCP region")
    parser.add_argument("--image", required=True, help="Container image URI (tag or digest)")
    parser.add_argument("--environment", required=True, help="Target environment (dev|staging|production)")
    parser.add_argument("--change-id", default=None, help="ServiceNow change ID")
    parser.add_argument("--dry-run", action="store_true", help="Validate inputs without deploying")
    parser.add_argument("--memory", default="256Mi", help="Memory allocation (e.g. 256Mi, 1Gi)")
    parser.add_argument("--cpu", default="1", help="CPU allocation (e.g. 1, 2)")
    parser.add_argument("--concurrency", type=int, default=80, help="Max concurrent requests per instance")
    parser.add_argument("--min-instances", type=int, default=0, help="Minimum instance count")
    parser.add_argument("--max-instances", type=int, default=100, help="Maximum instance count")
    parser.add_argument("--env-vars", default=None, help="Environment variables as KEY=VALUE,KEY=VALUE")
    parser.add_argument("--service-account", default=None, help="Service account email")
    parser.add_argument("--vpc-connector", default=None, help="VPC connector path")
    parser.add_argument("--ingress", default="all", help="Ingress setting (all|internal|internal-and-cloud-load-balancing)")
    args = parser.parse_args()

    # Validate all inputs
    try:
        svc = service_name(args.service)
        proj = gcp_project(args.project)
        rgn = region(args.region)
        img = image_uri(args.image)
        env = environment(args.environment)
        mem = validate_memory(args.memory)
        cp = validate_cpu(args.cpu)
        conc = validate_concurrency(args.concurrency)
        min_inst = validate_instances(args.min_instances, "min_instances")
        max_inst = validate_instances(args.max_instances, "max_instances")
        ing = validate_ingress(args.ingress)
    except ValueError as e:
        safe_error(str(e))

    parsed_env_vars = None
    if args.env_vars:
        try:
            parsed_env_vars = validate_env_vars(args.env_vars)
        except ValueError as e:
            safe_error(str(e))

    if args.service_account:
        try:
            validate_sa(args.service_account)
        except ValueError as e:
            safe_error(str(e))

    if args.vpc_connector:
        try:
            validate_vpc(args.vpc_connector)
        except ValueError as e:
            safe_error(str(e))

    if min_inst > max_inst:
        safe_error("E505: min_instances cannot exceed max_instances")

    audit = AuditClient(svc, env, proj)

    # Dry run: validate only
    if args.dry_run:
        audit.write("deploy_dry_run", {
            "status": "dry_run_complete",
            "image": img,
            "memory": mem,
            "cpu": cp,
            "concurrency": conc,
        })
        sanitized_print(f"STATUS=dry_run_complete")
        sanitized_print(f"SERVICE={svc}")
        sanitized_print(f"PROJECT={proj}")
        sanitized_print(f"REGION={rgn}")
        sanitized_print(f"IMAGE={img}")
        sanitized_print(f"ENVIRONMENT={env}")
        sanitized_print(f"AUDIT_LOG={audit.get_log_path()}")
        return

    # Deploy
    client = CloudRunClient(proj, rgn)
    result = client.deploy_revision(
        service=svc,
        image=img,
        memory=mem,
        cpu=cp,
        concurrency=conc,
        min_instances=min_inst,
        max_instances=max_inst,
        env_vars=parsed_env_vars,
        service_account=args.service_account,
        vpc_connector=args.vpc_connector,
        ingress=ing,
    )

    audit.write("deploy", {
        "status": result["status"],
        "revision": result["revision"],
        "image": img,
        "change_id": args.change_id,
    })

    sanitized_print(f"REVISION={result['revision']}")
    sanitized_print(f"STATUS={result['status']}")
    sanitized_print(f"SERVICE={svc}")
    sanitized_print(f"PROJECT={proj}")
    sanitized_print(f"REGION={rgn}")
    sanitized_print(f"URL={result['url']}")
    sanitized_print(f"AUDIT_LOG={audit.get_log_path()}")


if __name__ == "__main__":
    main()
