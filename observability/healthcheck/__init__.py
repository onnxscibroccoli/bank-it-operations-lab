"""Lightweight, stdlib-only host health collector with fail-closed decisions.

Scope: lab / reference code. Nothing here changes production endpoints or routing.
"""

__version__ = "0.1.0"

PAYLOAD_SCHEMA = "bank-it-lab/observability/health-payload/v1"
RESULT_SCHEMA = "bank-it-lab/observability/health-result/v1"

# Hard bounds shared by every module (fail closed when exceeded).
MAX_PROBES = 16
MAX_TIMEOUT_S = 10.0
DEFAULT_TIMEOUT_S = 2.0
MAX_BODY_BYTES = 65536
DEFAULT_BODY_BYTES = 4096
MAX_PAYLOAD_BYTES = 1_048_576

EXIT_HEALTHY = 0
EXIT_UNHEALTHY = 1
EXIT_MALFORMED = 2
