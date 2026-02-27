"""
Vault client — fetch secrets for internal use by scripts.

NEVER print returned values to stdout.
Use only within script process scope.
Credentials fetched here must not appear in any log, error message,
or output that Claude or any downstream consumer can read.
"""
import os
import re
import sys


def _validate_vault_path(path: str) -> str:
    """Reject paths with traversal sequences or invalid characters."""
    if '..' in path or '\x00' in path:
        raise RuntimeError("Invalid vault path: contains forbidden sequence")
    if not re.match(r'^[A-Za-z0-9/_\-\.]+$', path):
        raise RuntimeError("Invalid vault path: contains invalid characters")
    return path


def get_secret(path: str) -> str:
    """
    Fetch a secret from Vault by path.

    Uses VAULT_ADDR and VAULT_TOKEN env vars, or workload identity
    if available. The token itself is never printed.

    Returns the secret value as a string.
    Raises RuntimeError if the secret cannot be fetched.
    """
    _validate_vault_path(path)

    vault_addr = os.environ.get("VAULT_ADDR")
    vault_token = os.environ.get("VAULT_TOKEN")  # or use workload identity

    if not vault_addr:
        raise RuntimeError("VAULT_ADDR not set")

    # TODO: implement hvac or requests-based Vault call
    # STUB — PINNED
    raise NotImplementedError("vault_client not yet implemented")
