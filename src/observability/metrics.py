"""Basic metrics helpers (prometheus-compatible when installed)."""
try:
	from prometheus_client import Counter, Summary
	HAS_PROM = True
except Exception:
	HAS_PROM = False

from config.logging_config import logger


if HAS_PROM:
	AGENT_EXECUTIONS = Counter('agent_executions_total', 'Total agent executions', ['agent', 'status'])
	AGENT_LATENCY_MS = Summary('agent_latency_ms', 'Agent execution latency (ms)', ['agent'])
else:
	AGENT_EXECUTIONS = None
	AGENT_LATENCY_MS = None


def record_execution(agent_name: str, status: str, latency_ms: float):
	"""Record an execution metric if prometheus is available, otherwise log."""
	if HAS_PROM:
		try:
			AGENT_EXECUTIONS.labels(agent=agent_name, status=status).inc()
			AGENT_LATENCY_MS.labels(agent=agent_name).observe(latency_ms)
		except Exception as e:
			logger.debug(f"Prometheus metric record failed: {e}")
	else:
		logger.debug(f"Metric: {agent_name} status={status} latency_ms={latency_ms}")