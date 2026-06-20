# rate-limiter-service

> A standalone, production-grade Rate Limiting Service — supports multiple algorithms, multi-tenant, Redis-backed, with a REST API and real-time dashboard.

## Features

- 5 rate limiting algorithms (Fixed Window, Sliding Window Log, Sliding Window Counter, Token Bucket, Leaky Bucket)
- Multi-tenant support
- Redis-backed storage (with cluster support)
- In-memory store for development/testing
- REST API for rule management, analytics, and whitelist/blacklist
- Real-time dashboard (React frontend)
- Prometheus metrics
- Docker deployment
- Comprehensive test suite

## Quick Start

```bash
make run
```

## License

MIT
