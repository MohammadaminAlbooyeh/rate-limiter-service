# System Architecture

## Overview

The Rate Limiter Service is a distributed, multi-tenant rate limiting system designed for high throughput and low latency. It uses a layered architecture with clear separation of concerns.

## Layered Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          Client Layer                                   │
│                  (External Applications, Dashboards)                    │
└────────┬─────────────────────────────────────────────────────┬──────────┘
         │                                                      │
    ┌────▼────┐                                         ┌──────▼──────┐
    │ REST API │ (http://8000)                          │  Dashboard  │
    │ Clients  │                                        │  (:3000)    │
    └────┬────┘                                         └──────┬──────┘
         │                                                     │
         └────┬──────────────────────────────────────────────┬┘
              │                                              │
    ┌─────────▼──────────────────────────────────────────────▼──────────┐
    │                     Presentation Layer                             │
    │                                                                    │
    │  FastAPI Application                                             │
    │  ┌──────────────────────────────────────────────────────────┐   │
    │  │                  HTTP Endpoints                          │   │
    │  │  POST /api/v1/check           - Rate limit check        │   │
    │  │  GET  /api/v1/rules           - List rules              │   │
    │  │  POST /api/v1/rules           - Create rule             │   │
    │  │  PATCH /api/v1/rules/{id}     - Update rule             │   │
    │  │  DELETE /api/v1/rules/{id}    - Delete rule             │   │
    │  │  POST /api/v1/simulate        - Test rule               │   │
    │  │  POST /api/v1/lists/whitelist - Whitelist management    │   │
    │  │  POST /api/v1/lists/blacklist - Blacklist management    │   │
    │  │  GET  /api/v1/analytics       - Metrics                 │   │
    │  │  WS   /ws                     - Real-time updates       │   │
    │  └──────────────────────────────────────────────────────────┘   │
    │  ┌──────────────────────────────────────────────────────────┐   │
    │  │                  Middleware Stack                        │   │
    │  │  • Authentication (Admin Key validation)                │   │
    │  │  • CORS handling                                         │   │
    │  │  • Request logging                                       │   │
    │  │  • Error handling & response formatting                │   │
    │  └──────────────────────────────────────────────────────────┘   │
    └──────────────────┬───────────────────────────────────────────────┘
                       │
    ┌──────────────────▼───────────────────────────────────────────────┐
    │                     Application Layer                             │
    │                                                                   │
    │  Service Components (Async Python)                              │
    │  ┌──────────────────────────────────────────────────────────┐  │
    │  │  LimiterService                                          │  │
    │  │  • Orchestrates rate limit checks                       │  │
    │  │  • Routes to appropriate algorithm                      │  │
    │  │  • Manages store lifecycle                              │  │
    │  │  • Handles distributed state                            │  │
    │  └──────────────────────────────────────────────────────────┘  │
    │  ┌──────────────────────────────────────────────────────────┐  │
    │  │  RuleService                                             │  │
    │  │  • CRUD operations on rate limit rules                  │  │
    │  │  • Rule validation & conflict detection                │  │
    │  │  • Rule caching for performance                         │  │
    │  │  • Multi-tenant rule isolation                          │  │
    │  └──────────────────────────────────────────────────────────┘  │
    │  ┌──────────────────────────────────────────────────────────┐  │
    │  │  AnalyticsService                                        │  │
    │  │  • Aggregates rate limit metrics                        │  │
    │  │  • Computes timeline data for dashboard                │  │
    │  │  • Tracks violation trends                              │  │
    │  │  • Database query optimization                          │  │
    │  └──────────────────────────────────────────────────────────┘  │
    │  ┌──────────────────────────────────────────────────────────┐  │
    │  │  AlertService                                            │  │
    │  │  • Configurable alert policies                          │  │
    │  │  • Alert persistence to database                        │  │
    │  │  • Alert acknowledgment tracking                        │  │
    │  └──────────────────────────────────────────────────────────┘  │
    │  ┌──────────────────────────────────────────────────────────┐  │
    │  │  WhitelistService                                        │  │
    │  │  • Manages whitelist entries                            │  │
    │  │  • Manages blacklist entries                            │  │
    │  │  • Fast lookup optimization                             │  │
    │  │  • Multi-type identifier support (IP, API key, etc.)   │  │
    │  └──────────────────────────────────────────────────────────┘  │
    └──────────────────┬───────────────────────────────────────────────┘
                       │
    ┌──────────────────▼───────────────────────────────────────────────┐
    │                   Business Logic Layer                            │
    │                                                                   │
    │  Rate Limiting Algorithms (Pluggable Architecture)              │
    │                                                                   │
    │  ┌─────────────────┬─────────────────┬──────────────┬──────────┐ │
    │  │  Fixed Window   │  Sliding Window │ Token Bucket │  Leaky   │ │
    │  │  Algorithm      │  Log Algorithm  │  Algorithm   │  Bucket  │ │
    │  │                 │                 │              │          │ │
    │  │ Fast, memory-   │ Most accurate,  │ Handles      │ Smooths  │ │
    │  │ efficient. Grid │ prevents burst. │ bursts,      │ traffic  │ │
    │  │ boundary burst. │ Highest memory. │ good rate.   │ evenly.  │ │
    │  │                 │                 │              │          │ │
    │  └─────────────────┴─────────────────┴──────────────┴──────────┘ │
    │  ┌──────────────────────────────────────────────────────────┐    │
    │  │  Sliding Window Counter Algorithm                        │    │
    │  │  • Hybrid approach (counters + sliding calculation)     │    │
    │  │  • Balanced accuracy and memory usage                   │    │
    │  └──────────────────────────────────────────────────────────┘    │
    │                                                                   │
    │  All algorithms implement BaseAlgorithm interface:               │
    │  async def check(identity_key, capacity, window_size)           │
    │      -> (allowed: bool, remaining: int, reset_time: int)        │
    └──────────────────┬───────────────────────────────────────────────┘
                       │
    ┌──────────────────▼───────────────────────────────────────────────┐
    │                    Persistence Layer                              │
    │                                                                   │
    │  ┌─────────────────────────────┐  ┌───────────────────────────┐ │
    │  │   Redis Store (Stateful)    │  │  Memory Store (Dev/Test)  │ │
    │  │                             │  │                           │ │
    │  │ Primary Storage:            │  │ Volatile, in-process:     │ │
    │  │ • Request counters          │  │ • No persistence          │ │
    │  │ • Token buckets             │  │ • Single instance only    │ │
    │  │ • Metadata & timestamps     │  │ • Fast for unit tests     │ │
    │  │ • Distributed state         │  │ • Full algorithm support  │ │
    │  │                             │  │                           │ │
    │  │ Modes:                      │  └───────────────────────────┘ │
    │  │ • Standard Redis server     │                                 │
    │  │ • Redis Cluster (HA)        │                                 │
    │  │ • Pub/Sub for real-time     │                                 │
    │  │                             │                                 │
    │  └─────────────────────────────┘                                 │
    │                                                                   │
    │  ┌───────────────────────────────────────────────────────────┐  │
    │  │   PostgreSQL Database (Configuration & Audit)            │  │
    │  │                                                           │  │
    │  │   Tables:                                                 │  │
    │  │   • rules - Rate limit rule definitions                 │  │
    │  │   • alerts - Alert configurations and history           │  │
    │  │   • events - Audit trail of all operations              │  │
    │  │   • analytics - Historical metrics (optional snapshot)   │  │
    │  │                                                           │  │
    │  │   Usage:                                                  │  │
    │  │   • Persistent configuration storage                    │  │
    │  │   • Audit logging & compliance                          │  │
    │  │   • Analytics history                                    │  │
    │  │   • Alerts management                                    │  │
    │  └───────────────────────────────────────────────────────────┘  │
    └──────────────────┬───────────────────────────────────────────────┘
                       │
    ┌──────────────────▼───────────────────────────────────────────────┐
    │                   External Systems                                │
    │                                                                   │
    │  ┌──────────────┐  ┌──────────────┐  ┌────────────────────────┐ │
    │  │    Redis     │  │  PostgreSQL  │  │  Monitoring/Logging    │ │
    │  │   :6379      │  │   :5432      │  │  (Prometheus, ELK)     │ │
    │  └──────────────┘  └──────────────┘  └────────────────────────┘ │
    └────────────────────────────────────────────────────────────────┘
```

## Data Flow

### Rate Limit Check Flow

```
Client Request
    │
    ▼
┌─────────────────────────┐
│ HTTP POST /api/v1/check │
└────────────┬────────────┘
             │
             ▼
        ┌─────────────────────────────────────┐
        │ 1. Authentication Middleware         │
        │    (Validate API key if required)   │
        └──────────────┬──────────────────────┘
                       │
                       ▼
        ┌──────────────────────────────────────────────┐
        │ 2. Parse Request (IP, API Key, User ID, etc) │
        └──────────────┬───────────────────────────────┘
                       │
                       ▼
        ┌──────────────────────────────────────────────┐
        │ 3. WhitelistService.is_whitelisted()         │
        │    -> ALLOW (skip rate limit check)          │
        └──────────────┬───────────────────────────────┘
                       │
             NO        │         YES
            ┌──────────▼──────────┐
            │                     │
            ▼                     ▼
    ┌────────────────┐   ┌──────────────────┐
    │ Whitelist Hit  │   │ Return Allowed   │
    │ Continue       │   │ (remaining: ∞)   │
    └────────┬───────┘   └──────────────────┘
             │
             ▼
    ┌────────────────────────────────────────┐
    │ 4. WhitelistService.is_blacklisted()   │
    │    -> DENY (reject request)             │
    └────────────┬─────────────────────────────┘
                 │
        YES      │      NO
    ┌────────────▼──────────┐
    │                       │
    ▼                       ▼
┌──────────────┐   ┌─────────────────────────────────┐
│ Return 403   │   │ 5. RuleService.get_rules()      │
│ Forbidden    │   │    (Fetch all active rules)     │
└──────────────┘   └────────────┬────────────────────┘
                                │
                                ▼
                   ┌──────────────────────────────────────┐
                   │ 6. For Each Matching Rule:            │
                   │    - Identify algorithm              │
                   │    - Build identity key (tenant+id)  │
                   │    - Call Algorithm.check()          │
                   └────────────┬─────────────────────────┘
                                │
                                ▼
                   ┌──────────────────────────────────────┐
                   │ 7. Algorithm queries Redis Store:    │
                   │    - Get current state               │
                   │    - Update counters/tokens          │
                   │    - Persist to Redis                │
                   └────────────┬─────────────────────────┘
                                │
                                ▼
                   ┌──────────────────────────────────────┐
                   │ 8. Check Limit Decision:             │
                   │    allowed = (requests < limit)      │
                   │    remaining = (limit - requests)    │
                   │    reset = (next_window_time)        │
                   └────────────┬─────────────────────────┘
                                │
                         ALLOWED │ NOT ALLOWED
                              YES │ NO
                        ┌─────────▼──────────┐
                        │                    │
                        ▼                    ▼
            ┌─────────────────────┐  ┌──────────────────────┐
            │ Continue to next    │  │ Return 429           │
            │ rule (if more)      │  │ Too Many Requests    │
            │                     │  │ (remaining: 0)       │
            └──────────┬──────────┘  └──────────────────────┘
                       │
             All Passed │
                       ▼
            ┌─────────────────────┐
            │ Log event to DB     │
            │ Send to Analytics   │
            │ Return 200 OK       │
            └─────────────────────┘
```

## Multi-Tenant Isolation

```
┌─────────────────────────────────────────────────────────┐
│              Multi-Tenant Architecture                   │
└─────────────────────────────────────────────────────────┘

Request → Parse tenant_id from:
          • Subdomain (api.tenant1.example.com)
          • Header (X-Tenant-ID: tenant1)
          • URL path (/tenants/tenant1/check)
          • API key prefix

             ├─ Tenant A
             │  ├─ Rules (isolated)
             │  ├─ Whitelist/Blacklist (isolated)
             │  ├─ Redis Keys (prefixed: tenant_a:counter:key)
             │  └─ Database Records (tenant_id FK)
             │
             ├─ Tenant B
             │  ├─ Rules (isolated)
             │  ├─ Whitelist/Blacklist (isolated)
             │  ├─ Redis Keys (prefixed: tenant_b:counter:key)
             │  └─ Database Records (tenant_id FK)
             │
             └─ Tenant N
                └─ ...

Key Features:
✓ Logical isolation via prefixed Redis keys
✓ Database row-level filtering by tenant_id
✓ Independent rule sets per tenant
✓ Separate whitelist/blacklist per tenant
✓ Tenant-scoped analytics queries
✓ No cross-tenant data leakage
```

## Storage Strategies

### Redis Store (Production)

```
Redis Key Structure:
┌────────────────────────────────────┐
│ Format: {tenant}:{algorithm}:{key} │
├────────────────────────────────────┤
│ Example Keys:                      │
├────────────────────────────────────┤
│ tenant1:fixed_window:192.168.1.1   │
│ tenant1:token_bucket:api_key_123   │
│ tenant2:sliding_log:user_456       │
└────────────────────────────────────┘

Data Structures per Algorithm:
┌──────────────────┬────────────────────┐
│ Algorithm        │ Redis Structure    │
├──────────────────┼────────────────────┤
│ Fixed Window     │ String (counter)   │
│ Sliding Log      │ Sorted Set         │
│                  │ (timestamps)       │
│ Sliding Counter  │ Hash (counters +   │
│                  │ timestamp)         │
│ Token Bucket     │ Hash (tokens +     │
│                  │ last_refill)       │
│ Leaky Bucket     │ Hash (queue +      │
│                  │ leak_rate)         │
└──────────────────┴────────────────────┘

Expiration:
- Window-based: TTL = window_size + buffer
- Automatic cleanup via Redis TTL
- Prevents memory bloat
```

### PostgreSQL Database

```
Schema Overview:

┌──────────────┐     ┌──────────────┐
│   Rules      │     │   Alerts     │
├──────────────┤     ├──────────────┤
│ id (PK)      │     │ id (PK)      │
│ tenant_id    │     │ rule_id (FK) │
│ name         │     │ threshold    │
│ algorithm    │     │ enabled      │
│ capacity     │     │ created_at   │
│ window_size  │     │ updated_at   │
│ match_type   │     └──────────────┘
│ match_value  │
│ enabled      │     ┌──────────────┐
│ created_at   │     │   Events     │
│ updated_at   │     ├──────────────┤
└──────────────┘     │ id (PK)      │
                     │ type         │
                     │ entity_type  │
                     │ entity_id    │
                     │ data         │
                     │ timestamp    │
                     └──────────────┘

Whitelist/Blacklist Tables:
┌──────────────────┐
│ Whitelist Entries│
├──────────────────┤
│ id (PK)          │
│ tenant_id        │
│ identifier       │
│ type (ip, key)   │
│ created_at       │
└──────────────────┘

┌──────────────────┐
│ Blacklist Entries│
├──────────────────┤
│ id (PK)          │
│ tenant_id        │
│ identifier       │
│ type (ip, key)   │
│ reason           │
│ created_at       │
└──────────────────┘
```

## Real-Time Updates (WebSocket)

```
Dashboard ←→ WebSocket Server
                   │
                   ▼
            ┌──────────────┐
            │ Redis Pub/Sub│
            └──────────────┘
                   │
    ┌──────────────┼──────────────┐
    ▼              ▼              ▼
Updates        Analytics      Alerts
• Rule changes  • Request count • Limit violations
• Whitelist     • Trend data    • Config changes
• Alerts        • Performance   • Error events
```

## Deployment Topology

### Single Node

```
┌─────────────────────────────────────┐
│  Host Machine                       │
│  ┌─────────────────────────────────┤
│  │  Docker Compose                 │
│  │  ┌──────┐  ┌──────┐  ┌────────┐│
│  │  │ API  │  │Redis │  │Postgres││
│  │  │:8000 │  │:6379 │  │:5432   ││
│  │  └──────┘  └──────┘  └────────┘│
│  │  ┌─────────────────────────────┤
│  │  │ Frontend :3000              │
│  │  └─────────────────────────────┤
│  └─────────────────────────────────┘
└─────────────────────────────────────┘
```

### Kubernetes Cluster (HA)

```
┌────────────────────────────────────────────────────┐
│              Kubernetes Cluster                    │
├────────────────────────────────────────────────────┤
│                                                    │
│  ┌──────────────────────────────────────────────┐ │
│  │  API Deployment (3 replicas)                │ │
│  │  ┌─────────┬─────────┬─────────────────┐   │ │
│  │  │  Pod 1  │  Pod 2  │    Pod 3        │   │ │
│  │  │ :8000   │ :8000   │    :8000        │   │ │
│  │  └─────────┴─────────┴─────────────────┘   │ │
│  │       Load Balancer Service :80              │ │
│  └──────────────────────────────────────────────┘ │
│                    │                               │
│           ┌────────┼────────┐                      │
│           ▼        ▼        ▼                      │
│  ┌──────────────────────────────────────────────┐ │
│  │  Shared Services                             │ │
│  │  ┌────────────────┐  ┌────────────────────┐ │ │
│  │  │ Redis Cluster  │  │ PostgreSQL Replica │ │ │
│  │  │ (StatefulSet)  │  │ Set (3 nodes)      │ │ │
│  │  │ :6379          │  │ :5432              │ │ │
│  │  └────────────────┘  └────────────────────┘ │ │
│  └──────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────┘
```

## Performance Characteristics

### Algorithm Complexity

| Algorithm | Time | Space | Accuracy | Burst |
|-----------|------|-------|----------|-------|
| Fixed Window | O(1) | O(1) | Low | High |
| Sliding Log | O(n) | O(n) | High | None |
| Sliding Counter | O(1) | O(1) | Medium | Low |
| Token Bucket | O(1) | O(1) | High | Yes* |
| Leaky Bucket | O(1) | O(1) | High | No |

*Controlled burst

### Latency Targets

- Check request: < 10ms (p99)
- Redis round trip: < 5ms
- DB query: < 50ms
- Full check cycle: < 50ms (p99)

### Throughput Targets

- Single instance: 10K+ requests/sec
- Redis backend: 100K+ operations/sec
- Cluster mode: Linear scaling per node

## Security Architecture

```
┌──────────────────────────────────────┐
│     Security Layers                  │
├──────────────────────────────────────┤
│ 1. HTTPS/TLS (transport)             │
│    └─ All communication encrypted    │
│                                      │
│ 2. Authentication                    │
│    └─ Admin Key for /api/v1/admin    │
│    └─ API Key for client requests    │
│                                      │
│ 3. Rate Limiting (Meta)              │
│    └─ Admin endpoints rate limited   │
│    └─ Prevents abuse of management   │
│                                      │
│ 4. Input Validation                  │
│    └─ Request schema validation      │
│    └─ Sanitization of rule configs   │
│                                      │
│ 5. Database Security                 │
│    └─ Parameterized queries (SQLAlchemy ORM)
│    └─ Prepared statements            │
│    └─ No SQL injection vectors       │
│                                      │
│ 6. Data Isolation                    │
│    └─ Multi-tenant separation        │
│    └─ Tenant-scoped queries          │
│    └─ Redis key prefixing            │
│                                      │
│ 7. Audit Logging                     │
│    └─ All config changes logged      │
│    └─ Immutable event trail          │
└──────────────────────────────────────┘
```

## Extension Points

### Adding a Custom Algorithm

1. **Create Algorithm Class**
   ```python
   # backend/algorithms/custom_algo.py
   from backend.algorithms.base_algorithm import BaseAlgorithm
   
   class CustomAlgorithm(BaseAlgorithm):
       async def check(self, identity_key: str, capacity: int, window_size: int):
           # Implementation
           return allowed, remaining, reset_time
   ```

2. **Register in Factory**
   ```python
   # backend/algorithms/__init__.py
   ALGORITHMS["custom"] = CustomAlgorithm()
   ```

3. **Add Tests**
   ```python
   # tests/unit/test_custom_algo.py
   ```

4. **Use via API**
   ```json
   {
     "algorithm": "custom",
     "capacity": 100,
     "window_size": 3600
   }
   ```

### Adding Storage Backend

1. Implement `BaseStore` interface
2. Register in `LimiterService`
3. Support all algorithms

---

**Last Updated:** 2026-06-30
**Version:** 1.0
