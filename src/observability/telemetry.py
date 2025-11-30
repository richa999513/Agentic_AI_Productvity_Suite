"""Telemetry helpers (OTel-compatible when available)."""
try:
    from opentelemetry import trace
    HAS_OTEL = True
except Exception:
    HAS_OTEL = False

from config.logging_config import logger


def init_tracer(service_name: str = "aips"):
    if not HAS_OTEL:
        logger.debug("OpenTelemetry not installed; telemetry disabled.")
        return None
    tracer = trace.get_tracer(service_name)
    logger.debug("Telemetry tracer initialized")
    return tracer


def capture_exception(exc: Exception):
    logger.error(f"Captured exception: {exc}")