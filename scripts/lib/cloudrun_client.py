"""
Cloud Run client — wraps gcloud / Cloud Run Admin API calls.

PINNED — all methods return realistic stub data.
Actual implementation will use google-cloud-run SDK or gcloud CLI.
Credentials are sourced via ADC (Application Default Credentials)
and never printed to stdout.
"""
from datetime import datetime, timezone


class CloudRunClient:
    def __init__(self, project: str, region: str):
        self._project = project
        self._region = region

    def deploy_revision(
        self,
        service: str,
        image: str,
        revision_suffix: str = None,
        memory: str = "256Mi",
        cpu: str = "1",
        concurrency: int = 80,
        min_instances: int = 0,
        max_instances: int = 100,
        env_vars: dict = None,
        service_account: str = None,
        vpc_connector: str = None,
        ingress: str = "all",
    ) -> dict:
        """Deploy a new revision to a Cloud Run service."""
        # STUB — PINNED
        revision = revision_suffix or f"{service}-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}"
        return {
            "revision": revision,
            "service": service,
            "image": image,
            "status": "deployed",
            "url": f"https://{service}-{self._region}.a.run.app",
            "project": self._project,
            "region": self._region,
        }

    def get_service_status(self, service: str) -> dict:
        """Get current service status including traffic split."""
        # STUB — PINNED
        return {
            "service": service,
            "ready": True,
            "active_revision": f"{service}-20260227-120000",
            "traffic": [
                {"revision": f"{service}-20260227-120000", "percent": 100},
            ],
            "url": f"https://{service}-{self._region}.a.run.app",
            "project": self._project,
            "region": self._region,
        }

    def update_traffic(self, service: str, splits: list) -> dict:
        """
        Update traffic routing for a service.
        splits: list of {"revision": str, "percent": int}
        """
        # STUB — PINNED
        return {
            "service": service,
            "traffic": splits,
            "status": "traffic_updated",
            "project": self._project,
            "region": self._region,
        }

    def get_revisions(self, service: str, limit: int = 10) -> list:
        """List recent revisions for a service."""
        # STUB — PINNED
        return [
            {
                "name": f"{service}-20260227-120000",
                "image": f"gcr.io/{self._project}/{service}:v2",
                "created": "2026-02-27T12:00:00Z",
                "status": "active",
                "traffic_percent": 100,
            },
            {
                "name": f"{service}-20260226-100000",
                "image": f"gcr.io/{self._project}/{service}:v1",
                "created": "2026-02-26T10:00:00Z",
                "status": "retired",
                "traffic_percent": 0,
            },
        ]

    def check_health(self, service: str, endpoint: str = "/health") -> dict:
        """Check health of the active revision."""
        # STUB — PINNED
        return {
            "service": service,
            "endpoint": endpoint,
            "status_code": 200,
            "healthy": True,
            "latency_ms": 45,
        }

    def describe_revision(self, service: str, revision: str) -> dict:
        """Get detailed info about a specific revision."""
        # STUB — PINNED
        return {
            "name": revision,
            "service": service,
            "image": f"gcr.io/{self._project}/{service}:latest",
            "created": "2026-02-27T12:00:00Z",
            "status": "active",
            "memory": "256Mi",
            "cpu": "1",
            "concurrency": 80,
            "min_instances": 0,
            "max_instances": 100,
            "service_account": f"{service}-sa@{self._project}.iam.gserviceaccount.com",
            "ingress": "all",
            "project": self._project,
            "region": self._region,
        }
