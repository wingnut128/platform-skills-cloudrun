"""
Input validation for Cloud Run deployment skill.

All validators raise ValueError with an error code on failure.
Never echo raw invalid input in error messages.
"""
import re

# --- Allowlists ---

VALID_ENVIRONMENTS = {"dev", "staging", "production"}

VALID_REGIONS = {
    "us-central1", "us-east1", "us-east4", "us-west1", "us-west2",
    "us-south1", "europe-west1", "europe-west2", "europe-west3",
    "europe-west4", "europe-north1", "asia-east1", "asia-northeast1",
    "asia-southeast1", "australia-southeast1",
}

VALID_INGRESS = {"all", "internal", "internal-and-cloud-load-balancing"}

# --- Regex patterns ---

_SERVICE_NAME_RE = re.compile(r'^[a-z][a-z0-9-]{0,62}$')
_GCP_PROJECT_RE = re.compile(r'^[a-z][a-z0-9-]{4,28}[a-z0-9]$')
_IMAGE_TAG_RE = re.compile(
    r'^[a-z0-9._/-]+:[a-zA-Z0-9._-]{1,128}$'
)
_IMAGE_DIGEST_RE = re.compile(
    r'^[a-z0-9._/-]+@sha256:[a-f0-9]{64}$'
)
_CHANGE_ID_RE = re.compile(r'^CHG\d{7,15}$')
_REVISION_NAME_RE = re.compile(r'^[a-z][a-z0-9-]{0,95}$')
_SA_EMAIL_RE = re.compile(
    r'^[a-z][a-z0-9-]{4,28}@[a-z0-9.-]+\.iam\.gserviceaccount\.com$'
)
_VPC_CONNECTOR_RE = re.compile(
    r'^projects/[a-z][a-z0-9-]+/locations/[a-z0-9-]+/connectors/[a-z][a-z0-9-]+$'
)
_MEMORY_RE = re.compile(r'^(128|256|512)Mi$|^[1-8]Gi$')
_CPU_RE = re.compile(r'^[1248]$|^[12]\.0$|^0\.[1-9]$')
_ENV_VAR_RE = re.compile(r'^[A-Z_][A-Z0-9_]{0,255}$')

# Keys in env vars that suggest secrets
_SECRET_KEY_PATTERNS = [
    r'(?i)password', r'(?i)passwd', r'(?i)secret', r'(?i)token',
    r'(?i)api[_-]?key', r'(?i)credential', r'(?i)private[_-]?key',
]
_SECRET_KEY_COMPILED = [re.compile(p) for p in _SECRET_KEY_PATTERNS]


def service_name(value: str) -> str:
    if not _SERVICE_NAME_RE.match(value):
        raise ValueError("E001: Invalid service name format")
    return value


def gcp_project(value: str) -> str:
    if not _GCP_PROJECT_RE.match(value):
        raise ValueError("E002: Invalid GCP project ID format")
    return value


def region(value: str) -> str:
    if value not in VALID_REGIONS:
        raise ValueError("E003: Region not in allowlist")
    return value


def image_uri(value: str) -> str:
    if not (_IMAGE_TAG_RE.match(value) or _IMAGE_DIGEST_RE.match(value)):
        raise ValueError("E004: Invalid container image URI format")
    return value


def environment(value: str) -> str:
    if value not in VALID_ENVIRONMENTS:
        raise ValueError("E005: Environment not in allowlist")
    return value


def change_id(value: str) -> str:
    if not _CHANGE_ID_RE.match(value):
        raise ValueError("E100: Invalid change ID format")
    return value


def revision_name(value: str) -> str:
    if not _REVISION_NAME_RE.match(value):
        raise ValueError("E006: Invalid revision name format")
    return value


def service_account(value: str) -> str:
    if not _SA_EMAIL_RE.match(value):
        raise ValueError("E007: Invalid service account email format")
    return value


def vpc_connector(value: str) -> str:
    if not _VPC_CONNECTOR_RE.match(value):
        raise ValueError("E008: Invalid VPC connector format")
    return value


def ingress(value: str) -> str:
    if value not in VALID_INGRESS:
        raise ValueError("E009: Ingress setting not in allowlist")
    return value


def traffic_split(value: str) -> str:
    """Validate traffic split string: 'rev1=50,rev2=50'. Percentages must sum to 100."""
    parts = value.split(",")
    total = 0
    for part in parts:
        if "=" not in part:
            raise ValueError("E400: Invalid traffic split format, expected revision=percentage")
        rev, pct = part.split("=", 1)
        revision_name(rev.strip())
        try:
            p = int(pct.strip())
        except ValueError:
            raise ValueError("E401: Traffic percentage must be an integer")
        if p < 0 or p > 100:
            raise ValueError("E402: Traffic percentage must be 0-100")
        total += p
    if total != 100:
        raise ValueError("E403: Traffic percentages must sum to 100")
    return value


def env_vars(value: str) -> dict:
    """Validate KEY=VALUE pairs. Rejects keys that look like secret names (E501)."""
    result = {}
    for pair in value.split(","):
        pair = pair.strip()
        if not pair:
            continue
        if "=" not in pair:
            raise ValueError("E500: Invalid env var format, expected KEY=VALUE")
        key, val = pair.split("=", 1)
        if not _ENV_VAR_RE.match(key):
            raise ValueError("E500: Invalid environment variable key format")
        for pattern in _SECRET_KEY_COMPILED:
            if pattern.search(key):
                raise ValueError(
                    "E501: Environment variable key suggests a secret. "
                    "Use Secret Manager references instead"
                )
        result[key] = val
    return result


def memory(value: str) -> str:
    if not _MEMORY_RE.match(value):
        raise ValueError("E502: Invalid memory format (e.g. 256Mi, 1Gi)")
    return value


def cpu(value: str) -> str:
    if not _CPU_RE.match(value):
        raise ValueError("E503: Invalid CPU format (e.g. 1, 2, 0.5)")
    return value


def concurrency(value: int) -> int:
    if not (1 <= value <= 1000):
        raise ValueError("E504: Concurrency must be between 1 and 1000")
    return value


def instances(value: int, param_name: str = "instances") -> int:
    if not (0 <= value <= 1000):
        raise ValueError(f"E505: {param_name} must be between 0 and 1000")
    return value
