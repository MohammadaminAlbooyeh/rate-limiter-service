# Rate Limiter Service

A production-grade, distributed rate limiting service with support for multiple algorithms, multi-tenant isolation, and real-time monitoring. Built with FastAPI, Redis, and PostgreSQL.

**Key Features:** 5 algorithms • Multi-tenant • Redis/Cluster support • REST API • Real-time dashboard • Prometheus metrics • Docker-ready

## Table of Contents

- [Quick Start](#quick-start)
- [System Architecture](#system-architecture)
- [Features](#features)
- [Installation](#installation)
- [Configuration](#configuration)
- [API Documentation](#api-documentation)
- [Rate Limiting Algorithms](#rate-limiting-algorithms)
- [Examples](#examples)
- [Development](#development)
- [Testing](#testing)
- [License](#license)

## Quick Start

### Using Docker Compose (Recommended)

```bash
make run
```

This starts:
- **Backend API** at `http://localhost:8000`
- **Frontend Dashboard** at `http://localhost:3000`
- **Redis** for rate limit state
- **PostgreSQL** for persistence

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run database migrations
alembic upgrade head

# Start the API (with hot reload)
make dev
```

## System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Client Applications                      │
└────────────┬──────────────────────────────────────┬──────────┘
             │                                      │
      ┌──────▼──────┐                        ┌──────▼──────┐
      │  REST API   │                        │  Dashboard  │
      │  (:8000)    │                        │  (:3000)    │
      └──────┬──────┘                        └──────┬──────┘
             │                                      │
      ┌──────▼──────────────────────────────────────▼──────┐
      │           FastAPI Application                       │
      │  ┌────────────────────────────────────────────┐    │
      │  │         API Routes & Middleware            │    │
      │  │  - Rate Limit Check (/api/v1/check)      │    │
      │  │  - Rule Management (/api/v1/rules)       │    │
      │  │  - Analytics (/api/v1/analytics)         │    │
      │  │  - Whitelist/Blacklist (/api/v1/lists)  │    │
      │  │  - Simulation (/api/v1/simulate)         │    │
      │  └────────────────────────────────────────────┘    │
      │  ┌────────────────────────────────────────────┐    │
      │  │            Service Layer                   │    │
      │  │  - LimiterService (checks limits)         │    │
      │  │  - RuleService (manages rules)            │    │
      │  │  - AnalyticsService (tracks metrics)      │    │
      │  │  - AlertService (notifications)           │    │
      │  │  - WhitelistService (lists management)    │    │
      │  └────────────────────────────────────────────┘    │
      │  ┌────────────────────────────────────────────┐    │
      │  │         Algorithm Layer                    │    │
      │  │  - Fixed Window                           │    │
      │  │  - Sliding Window Log                     │    │
      │  │  - Sliding Window Counter                 │    │
      │  │  - Token Bucket                           │    │
      │  │  - Leaky Bucket                           │    │
      │  └────────────────────────────────────────────┘    │
      └──────┬──────────────────────────────────────┬───────┘
             │                                      │
      ┌──────▼──────┐                        ┌──────▼─────────┐
      │ PostgreSQL  │                        │  Redis Store   │
      │ (Persistence)                        │  (State)       │
      │             │                        │                │
      │ - Rules     │                        │ - Counters     │
      │ - Alerts    │                        │ - Tokens       │
      │ - Events    │                        │ - Metadata     │
      │ - Analytics │                        │ (Cluster mode) │
      └─────────────┘                        └────────────────┘
```

### Components

| Component | Purpose | Technology |
|-----------|---------|------------|
| **API Server** | HTTP endpoints for rate limit checks, rule management, and analytics | FastAPI + Uvicorn |
| **Services** | Business logic layer for rate limiting, rules, alerts, and analytics | Python async |
| **Algorithms** | 5 rate limiting implementations with pluggable interface | Python |
| **Storage** | Persistent state for counters, tokens, and metadata | Redis/Redis Cluster |
| **Database** | Persistent storage for configuration and audit trail | PostgreSQL + SQLAlchemy |
| **Frontend** | Real-time dashboard for monitoring and configuration | React + WebSocket |
| **Middleware** | Request authentication, rate limit application, CORS | FastAPI middleware |

## Features

### Core Rate Limiting
- **5 Algorithms**: Fixed Window, Sliding Window Log, Sliding Window Counter, Token Bucket, Leaky Bucket
- **Multi-Tenant**: Isolation per tenant with independent rule sets
- **Flexible Matching**: Match requests by IP, API key, user ID, endpoint, or HTTP method
- **Pluggable**: Easily add custom algorithms

### Storage & Scalability
- **Redis-Backed**: Fast, distributed state management
- **Cluster Mode**: Support for Redis Cluster deployments
- **In-Memory**: Development/testing with MemoryStore
- **Async/Await**: Non-blocking I/O throughout

### API & Monitoring
- **REST API**: Full-featured endpoints for all operations
- **WebSocket**: Real-time dashboard updates
- **Analytics**: Detailed metrics on rate limit usage
- **Prometheus Metrics**: Integration-ready for monitoring stacks
- **Alerts**: Configurable alerts for limit violations
- **Audit Trail**: Event logging to database

### Management
- **Admin Dashboard**: React-based UI for rule and list management
- **Whitelist/Blacklist**: Bypass or block specific identities
- **Simulation**: Test rules before deployment
- **CRUD Operations**: Full lifecycle management for rules and alerts

## Installation

### Prerequisites
- Python 3.10+
- Docker & Docker Compose (for containerized deployment)
- Redis 6.0+ (or Redis Cluster)
- PostgreSQL 13+

### Option 1: Docker Compose (Recommended)

```bash
# Clone repository
git clone <repository-url>
cd rate-limiter-service

# Start all services
docker-compose up --build

# Verify services
curl http://localhost:8000/health
# Check dashboard at http://localhost:3000
```

### Option 2: Local Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Create .env file
cat > .env << EOF
DATABASE_URL=postgresql+asyncpg://user:pass@localhost/ratelimiter
REDIS_HOST=localhost
REDIS_PORT=6379
LOG_LEVEL=INFO
EOF

# Initialize database
alembic upgrade head

# Start API (development)
make dev

# In another terminal, start frontend
cd frontend && npm start
```

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | - | PostgreSQL connection string (required) |
| `REDIS_HOST` | `localhost` | Redis server host |
| `REDIS_PORT` | `6379` | Redis server port |
| `USE_REDIS` | `true` | Enable Redis as storage backend |
| `USE_REDIS_CLUSTER` | `false` | Enable Redis Cluster mode |
| `REDIS_CLUSTER_NODES` | - | Comma-separated cluster nodes (e.g., `node1:6379,node2:6379`) |
| `LOG_LEVEL` | `INFO` | Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL) |
| `ADMIN_KEY` | - | Secret key for admin endpoints |
| `CORS_ORIGINS` | `*` | Allowed CORS origins |

### Example Production Configuration

```bash
export DATABASE_URL=postgresql+asyncpg://ratelimit:secure_password@prod-db.aws.com/ratelimiter
export REDIS_HOST=prod-redis-cluster.aws.com
export REDIS_PORT=6379
export USE_REDIS_CLUSTER=true
export REDIS_CLUSTER_NODES=redis-node1:6379,redis-node2:6379,redis-node3:6379
export LOG_LEVEL=WARNING
export ADMIN_KEY=your-secure-admin-key
```

## API Documentation

### Base URL
```
http://localhost:8000/api/v1
```

### Core Endpoints

#### Check Rate Limit
```http
POST /check
Content-Type: application/json

{
  "ip": "192.168.1.1",
  "api_key": "key_123",
  "user_id": "user_456",
  "endpoint": "/api/users",
  "method": "GET"
}
```

**Response (Allowed):**
```json
{
  "allowed": true,
  "remaining": 45,
  "reset": 1625097600
}
```

**Response (Blocked):**
```json
{
  "status_code": 429,
  "detail": "Rate limit exceeded"
}
```

#### Rule Management

**Create Rule:**
```http
POST /rules
Content-Type: application/json
X-Admin-Key: your-admin-key

{
  "name": "API Quota",
  "algorithm": "sliding_window_counter",
  "capacity": 100,
  "window_size": 3600,
  "match_type": "endpoint",
  "match_value": "/api/users",
  "enabled": true
}
```

**Get All Rules:**
```http
GET /rules
```

**Update Rule:**
```http
PATCH /rules/{rule_id}
X-Admin-Key: your-admin-key

{
  "capacity": 200
}
```

**Delete Rule:**
```http
DELETE /rules/{rule_id}
X-Admin-Key: your-admin-key
```

#### Whitelist/Blacklist

**Add to Whitelist:**
```http
POST /lists/whitelist
X-Admin-Key: your-admin-key

{
  "identifier": "192.168.1.1",
  "type": "ip"
}
```

**Add to Blacklist:**
```http
POST /lists/blacklist
X-Admin-Key: your-admin-key

{
  "identifier": "192.168.1.100",
  "type": "ip"
}
```

#### Analytics

**Get Analytics:**
```http
GET /analytics?start_time=1625000000&end_time=1625100000
```

**Response:**
```json
{
  "total_requests": 45000,
  "limited_requests": 123,
  "limit_rate": 0.27,
  "timeline": [
    {
      "timestamp": 1625000000,
      "request_count": 450,
      "limited_count": 2
    }
  ]
}
```

#### Simulation

**Test a Rule:**
```http
POST /simulate
Content-Type: application/json

{
  "ip": "192.168.1.1",
  "api_key": null,
  "user_id": null,
  "endpoint": "/api/users",
  "method": "GET",
  "rule": {
    "algorithm": "token_bucket",
    "capacity": 100,
    "window_size": 3600
  }
}
```

### Health Check
```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "redis": "connected",
  "database": "connected"
}
```

## Rate Limiting Algorithms

### Fixed Window
- **Description**: Divides time into fixed intervals; allows N requests per interval
- **Use Case**: Simple, predictable limits (e.g., 1000 requests per hour)
- **Pros**: O(1) memory, simple to understand
- **Cons**: Burst at window boundaries

```json
{
  "algorithm": "fixed_window",
  "capacity": 100,
  "window_size": 3600
}
```

### Sliding Window Log
- **Description**: Tracks exact timestamp of each request; allows N in last W seconds
- **Use Case**: Strict, burst-preventing limits
- **Pros**: Most accurate, no boundary burst
- **Cons**: O(n) memory for requests

```json
{
  "algorithm": "sliding_window_log",
  "capacity": 100,
  "window_size": 3600
}
```

### Sliding Window Counter
- **Description**: Hybrid approach combining counters with sliding calculation
- **Use Case**: Good accuracy with reasonable memory usage
- **Pros**: Balanced accuracy and memory
- **Cons**: Slightly less accurate than log-based

```json
{
  "algorithm": "sliding_window_counter",
  "capacity": 100,
  "window_size": 3600
}
```

### Token Bucket
- **Description**: Tokens accumulate over time; each request consumes a token
- **Use Case**: Allowing bursty traffic with average rate limit
- **Pros**: Handles bursts smoothly, predictable average rate
- **Cons**: Complex state management

```json
{
  "algorithm": "token_bucket",
  "capacity": 100,
  "window_size": 3600
}
```

### Leaky Bucket
- **Description**: Requests queue and drain at fixed rate
- **Use Case**: Smoothing traffic spikes uniformly
- **Pros**: Smooth traffic shaping, predictable outflow
- **Cons**: May reject during traffic spike

```json
{
  "algorithm": "leaky_bucket",
  "capacity": 100,
  "window_size": 3600
}
```

## Examples

### Basic Rate Limiting

```python
from backend.services.limiter_service import LimiterService
from backend.storage.redis_store import RedisStore
from backend.models.rule import Rule

# Initialize
store = RedisStore()
limiter = LimiterService(store=store)

# Define rule
rule = Rule(
    name="API Limit",
    algorithm="token_bucket",
    capacity=100,
    window_size=3600
)

# Check rate limit
identity = {
    "ip": "192.168.1.1",
    "endpoint": "/api/users"
}

allowed, remaining, reset = await limiter.check(identity, rule)
if not allowed:
    print(f"Rate limited! Reset at {reset}")
```

### Multi-Tenant Setup

```python
# Each tenant gets isolated rules
tenant_rules = {
    "tenant_1": [fixed_window_rule, token_bucket_rule],
    "tenant_2": [sliding_window_rule]
}

# Rules are matched independently per tenant
```

### Custom Algorithm

```python
from backend.algorithms.base_algorithm import BaseAlgorithm

class MyCustomAlgorithm(BaseAlgorithm):
    async def check(self, identity_key: str, capacity: int, window_size: int) -> tuple[bool, int, int]:
        # Your implementation
        return allowed, remaining, reset_time
```

## Development

### Project Structure

```
rate-limiter-service/
├── backend/
│   ├── algorithms/         # Rate limiting implementations
│   ├── api/               # REST endpoints
│   ├── middleware/        # Request middleware
│   ├── models/            # Data models & database
│   ├── services/          # Business logic
│   ├── storage/           # Storage backends (Redis, Memory)
│   ├── utils/             # Utilities (config, logging, WebSocket)
│   └── main.py            # FastAPI application
├── frontend/              # React dashboard
│   ├── src/
│   │   ├── components/    # React components
│   │   ├── pages/         # Page components
│   │   └── App.js         # Main app
│   └── Dockerfile
├── tests/
│   ├── unit/             # Unit tests
│   └── integration/       # Integration tests
├── alembic/              # Database migrations
├── requirements.txt      # Python dependencies
└── docker-compose.yml    # Docker configuration
```

### Setup Development Environment

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install development tools
pip install pytest pytest-cov ruff

# Start Redis and PostgreSQL
docker-compose up redis postgres -d

# Run migrations
alembic upgrade head

# Start development server
make dev
```

### Code Quality

```bash
# Lint code
make lint

# Run tests with coverage
make test

# Clean up
make clean
```

### Adding a New Algorithm

1. Create file: `backend/algorithms/my_algorithm.py`
2. Implement `BaseAlgorithm` interface
3. Register in `backend/algorithms/__init__.py`
4. Add unit tests in `tests/unit/test_my_algorithm.py`
5. Test via `/simulate` endpoint

## Testing

### Run All Tests

```bash
make test
```

### Run Specific Test Suite

```bash
pytest tests/unit/test_sliding_window_counter.py -v
pytest tests/integration/test_redis_store.py -v
```

### Test Coverage

```bash
pytest tests/ --cov=backend --cov-report=html
open htmlcov/index.html
```

### Key Test Suites
- `test_*_algorithm.py` - Individual algorithm correctness
- `test_limiter_service.py` - Core rate limiting logic
- `test_redis_store.py` - Redis persistence
- `test_analytics_service.py` - Metrics calculation
- `test_whitelist_service.py` - List management

## Deployment

### Docker Image

```bash
# Build
docker build -t rate-limiter:latest .

# Run
docker run -p 8000:8000 \
  -e DATABASE_URL=postgresql://... \
  -e REDIS_HOST=redis.example.com \
  rate-limiter:latest
```

### Kubernetes Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: rate-limiter-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: rate-limiter-api
  template:
    metadata:
      labels:
        app: rate-limiter-api
    spec:
      containers:
      - name: api
        image: rate-limiter:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: rate-limiter-secrets
              key: database-url
        - name: REDIS_HOST
          value: redis-cluster.default.svc.cluster.local
```

## Monitoring & Observability

### Prometheus Metrics

```
# Rate limit metrics
ratelimit_check_total{algorithm,match_type} - Total checks
ratelimit_limited_total{algorithm} - Total limited requests
ratelimit_check_duration_seconds - Check latency
```

### Dashboard Metrics

- Real-time request rate
- Limit violation rate
- Per-rule statistics
- Per-tenant usage

### Logs

- All API requests
- Rate limit decisions
- Algorithm state changes
- Database migrations

## License

MIT
