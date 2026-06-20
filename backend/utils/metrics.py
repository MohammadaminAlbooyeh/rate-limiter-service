from prometheus_client import Counter, Histogram

REQUEST_COUNT = Counter(
    "ratelimiter_requests_total",
    "Total number of requests processed by the rate limiter",
    ["identity", "endpoint", "method", "status"] # status can be "allowed", "blocked", "blacklisted", "whitelisted"
)

LATENCY = Histogram(
    "ratelimiter_check_latency_seconds",
    "Latency of rate limiter checks in seconds"
)
