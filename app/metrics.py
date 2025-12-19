from prometheus_client import Counter, Gauge, Histogram

operations_created_total = Counter(
    "operations_created_total",
    "Total number of operations created"
)

operations_succeeded_total = Counter(
    "operation_succeeded_total",
    "Total number of operations completed successfully"
)

operations_failed_total = Counter(
    "operation_failed_total",
    "Total number of operations that failed"
)

operations_running = Gauge(
    "operation_running",
    "Number of operations currently running"
)

operations_duration_seconds = Histogram(
    "operation_duration_seconds",
    "Time spent executing operations"
)