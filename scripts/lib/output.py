"""
Sanitized output helper.

Scrubs values that look like credentials before printing to stdout.
Use for any dynamic content that might have passed through a code path
touching secrets — error messages, exception strings, config summaries.
"""
import re
import sys

# Patterns that suggest a value contains a credential
_CREDENTIAL_PATTERNS = [
    r"(?i)(password|passwd|pwd)\s*[=:]\s*\S+",
    r"(?i)(token|api[_-]?key|secret|credential)\s*[=:]\s*\S+",
    r"(?i)bearer\s+[A-Za-z0-9\-._~+/]+=*",
    r"(?i)aws[_-]?(secret|access)[_-]?key\s*[=:]\s*\S+",
    r"[A-Za-z0-9+/]{40,}={0,2}",  # long base64 strings
]

_COMPILED = [re.compile(p) for p in _CREDENTIAL_PATTERNS]


def sanitize(text: str) -> str:
    """Replace potential credential values with [REDACTED]."""
    for pattern in _COMPILED:
        text = pattern.sub("[REDACTED]", text)
    return text


def sanitized_print(text: str):
    """Print to stdout after sanitization."""
    print(sanitize(str(text)))


def safe_error(message: str):
    """Print sanitized error message and exit 1."""
    sanitized_print(f"ERROR={sanitize(message)}")
    sys.exit(1)
