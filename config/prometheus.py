"""
Prometheus metrics configuration.

This module configures Prometheus metrics for the FastAPI application.
"""

from prometheus_client import Counter, Gauge, Histogram
from prometheus_fastapi_instrumentator import Instrumentator

# Request metrics
http_requests_total = Counter(
    "http_requests_total", "Total number of HTTP requests", ["method", "endpoint", "status"]
)

http_request_duration_seconds = Histogram(
    "http_request_duration_seconds", "HTTP request duration in seconds", ["method", "endpoint"]
)

# Database metrics
db_connections_active = Gauge("db_connections_active", "Number of active database connections")

db_queries_total = Counter(
    "db_queries_total", "Total number of database queries", ["operation", "table"]
)

# Business metrics
users_total = Gauge("users_total", "Total number of users in the system")


def setup_prometheus_metrics(app):
    """
    Setup Prometheus metrics for the FastAPI app.

    Usage:
        from config.prometheus import setup_prometheus_metrics
        setup_prometheus_metrics(app)
    """
    Instrumentator().instrument(app).expose(app, endpoint="/metrics")
