"""
Simplified audit client — writes JSON lines to local files.

Each deployment session gets its own log file:
  ./audit/<service>-<env>-<timestamp>.jsonl
"""
import json
import os
import re
import time
from datetime import datetime, timezone
from pathlib import Path


_AUDIT_DIR = Path(__file__).resolve().parent.parent.parent / "audit"

# Prevent path traversal in service/env names
_SAFE_NAME_RE = re.compile(r'^[a-z0-9-]+$')


class AuditClient:
    def __init__(self, service: str, env: str, project: str):
        if not _SAFE_NAME_RE.match(service):
            raise ValueError("Invalid service name for audit path")
        if not _SAFE_NAME_RE.match(env):
            raise ValueError("Invalid environment for audit path")

        self._service = service
        self._env = env
        self._project = project
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        self._filename = f"{service}-{env}-{timestamp}.jsonl"
        self._path = _AUDIT_DIR / self._filename

        # Validate resolved path is inside audit directory
        resolved = self._path.resolve()
        if not str(resolved).startswith(str(_AUDIT_DIR.resolve())):
            raise ValueError("Audit path escapes audit directory")

        _AUDIT_DIR.mkdir(parents=True, exist_ok=True)

    def write(self, step: str, record: dict):
        """Append a JSON line to the audit log."""
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "service": self._service,
            "environment": self._env,
            "project": self._project,
            "step": step,
            **record,
        }
        with open(self._path, "a") as f:
            f.write(json.dumps(entry, default=str) + "\n")

    def get_log_path(self) -> str:
        """Return the path to the audit log file."""
        return str(self._path)
