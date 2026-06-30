# Deployment Guide

## Quick Reference

| Deployment | Scale | Availability | Complexity | Cost |
|------------|-------|--------------|-----------|------|
| Docker Compose | Single node | ❌ None | ⭐ Low | ⭐ Low |
| Kubernetes | Multi-node | ✅ High | ⭐⭐⭐ High | ⭐⭐ Medium |
| AWS ECS | Multi-node | ✅ High | ⭐⭐ Medium | ⭐⭐ Medium |

## Deployment Topologies

### 1. Docker Compose (Development/Testing)

**Best For:** Local development, CI/CD testing, small deployments

```
┌─────────────────────────────────────┐
│       Host Machine                  │
├─────────────────────────────────────┤
│  docker-compose up --build          │
│                                     │
│  ┌─────────────────────────────┐   │
│  │ rate-limiter-api            │   │
│  │ (FastAPI + Python)          │   │
│  │ :8000 → host:8000           │   │
│  └─────────────────────────────┘   │
│                                     │
│  ┌─────────────────────────────┐   │
│  │ redis (7-alpine)            │   │
│  │ :6379 → host:6379           │   │
│  └─────────────────────────────┘   │
│                                     │
│  ┌─────────────────────────────┐   │
│  │ postgres (16-alpine)        │   │
│  │ :5432 → host:5432           │   │
│  │ ratelimiter DB              │   │
│  └─────────────────────────────┘   │
│                                     │
│  ┌─────────────────────────────┐   │
│  │ rate-limiter-frontend       │   │
│  │ (React + Nginx)             │   │
│  │ :3000 → host:3000           │   │
│  └─────────────────────────────┘   │
└─────────────────────────────────────┘
```

**Setup:**
```bash
git clone <repo>
cd rate-limiter-service
docker-compose up --build
```

**Verify:**
```bash
curl http://localhost:8000/health
# Navigate to http://localhost:3000
```

**Cleanup:**
```bash
docker-compose down -v  # Remove volumes too
```

### 2. Kubernetes Deployment (Production HA)

**Best For:** Production workloads, high availability, auto-scaling

#### Architecture

```
┌────────────────────────────────────────────────────────────┐
│                  Kubernetes Cluster                        │
│                                                            │
│  Ingress Controller (nginx-ingress, AWS ALB, etc.)        │
│         ↓ (HTTP/HTTPS)                                    │
│                                                            │
│  ┌──────────────────────────────────────────────────────┐ │
│  │  rate-limiter Service (type: LoadBalancer)           │ │
│  │  Selector: app=rate-limiter-api                      │ │
│  │  ┌────────────────────────────────────────────────┐ │ │
│  │  │  Deployment: rate-limiter-api                 │ │ │
│  │  │  Replicas: 3                                  │ │ │
│  │  │  └────────────────────────────────────────┐  │ │ │
│  │  │    ┌──────────────────────────────────┐  │  │ │ │
│  │  │    │ Pod 1                            │  │  │ │ │
│  │  │    │ Container: rate-limiter:v1.0     │  │  │ │ │
│  │  │    │ Port: 8000                       │  │  │ │ │
│  │  │    │ Resources:                       │  │  │ │ │
│  │  │    │  CPU: 500m | Memory: 512Mi       │  │  │ │ │
│  │  │    │ Readiness Probe: /health         │  │  │ │ │
│  │  │    │ Liveness Probe: /health          │  │  │ │ │
│  │  │    └──────────────────────────────────┘  │  │ │ │
│  │  │    ┌──────────────────────────────────┐  │  │ │ │
│  │  │    │ Pod 2                            │  │  │ │ │
│  │  │    │ (identical)                      │  │  │ │ │
│  │  │    └──────────────────────────────────┘  │  │ │ │
│  │  │    ┌──────────────────────────────────┐  │  │ │ │
│  │  │    │ Pod 3                            │  │  │ │ │
│  │  │    │ (identical)                      │  │  │ │ │
│  │  │    └──────────────────────────────────┘  │  │ │ │
│  │  └────────────────────────────────────────────┘  │ │ │
│  └──────────────────────────────────────────────────┘ │
│                                                        │
│  ┌──────────────────────────────────────────────────┐ │
│  │  External Services (StatefulSets)               │ │
│  │                                                  │ │
│  │  Redis Cluster (3 nodes)                        │ │
│  │  ├─ redis-0.redis.default.svc.cluster.local    │ │
│  │  ├─ redis-1.redis.default.svc.cluster.local    │ │
│  │  └─ redis-2.redis.default.svc.cluster.local    │ │
│  │                                                  │ │
│  │  PostgreSQL (with replication)                  │ │
│  │  ├─ postgres-primary                           │ │
│  │  └─ postgres-replica                           │ │
│  │                                                  │ │
│  └──────────────────────────────────────────────────┘ │
│                                                        │
│  ┌──────────────────────────────────────────────────┐ │
│  │  Monitoring & Logging                           │ │
│  │  ├─ Prometheus (metrics scraping)               │ │
│  │  ├─ Grafana (dashboards)                        │ │
│  │  └─ ELK Stack (log aggregation)                 │ │
│  └──────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────┘
```

#### Kubernetes Manifests

**1. Namespace**
```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: rate-limiter
```

**2. ConfigMap (Configuration)**
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: rate-limiter-config
  namespace: rate-limiter
data:
  LOG_LEVEL: "INFO"
  USE_REDIS: "true"
  USE_REDIS_CLUSTER: "true"
  REDIS_CLUSTER_NODES: "redis-0:6379,redis-1:6379,redis-2:6379"
  CORS_ORIGINS: "https://dashboard.example.com"
```

**3. Secret (Sensitive Data)**
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: rate-limiter-secrets
  namespace: rate-limiter
type: Opaque
stringData:
  DATABASE_URL: postgresql+asyncpg://user:password@postgres:5432/ratelimiter
  ADMIN_KEY: super-secret-admin-key-change-in-production
```

**4. Deployment**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: rate-limiter-api
  namespace: rate-limiter
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  selector:
    matchLabels:
      app: rate-limiter-api
  template:
    metadata:
      labels:
        app: rate-limiter-api
      annotations:
        prometheus.io/scrape: "true"
        prometheus.io/port: "8000"
        prometheus.io/path: "/metrics"
    spec:
      serviceAccountName: rate-limiter-sa
      containers:
      - name: api
        image: rate-limiter:v1.0
        imagePullPolicy: IfNotPresent
        ports:
        - name: http
          containerPort: 8000
          protocol: TCP
        
        env:
        - name: LOG_LEVEL
          valueFrom:
            configMapKeyRef:
              name: rate-limiter-config
              key: LOG_LEVEL
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: rate-limiter-secrets
              key: DATABASE_URL
        - name: REDIS_CLUSTER_NODES
          valueFrom:
            configMapKeyRef:
              name: rate-limiter-config
              key: REDIS_CLUSTER_NODES
        - name: ADMIN_KEY
          valueFrom:
            secretKeyRef:
              name: rate-limiter-secrets
              key: ADMIN_KEY
        
        resources:
          requests:
            cpu: 500m
            memory: 512Mi
          limits:
            cpu: 1000m
            memory: 1Gi
        
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
          timeoutSeconds: 5
          failureThreshold: 3
        
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 5
          timeoutSeconds: 3
          failureThreshold: 2
        
        securityContext:
          runAsNonRoot: true
          runAsUser: 1000
          allowPrivilegeEscalation: false
          readOnlyRootFilesystem: true
          capabilities:
            drop:
            - ALL
```

**5. Service**
```yaml
apiVersion: v1
kind: Service
metadata:
  name: rate-limiter-api
  namespace: rate-limiter
spec:
  type: LoadBalancer
  selector:
    app: rate-limiter-api
  ports:
  - name: http
    port: 80
    targetPort: 8000
    protocol: TCP
```

**6. Horizontal Pod Autoscaler**
```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: rate-limiter-hpa
  namespace: rate-limiter
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: rate-limiter-api
  minReplicas: 3
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

**Apply to Cluster:**
```bash
kubectl apply -f namespace.yaml
kubectl apply -f configmap.yaml
kubectl apply -f secret.yaml
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml
kubectl apply -f hpa.yaml

# Verify
kubectl get pods -n rate-limiter
kubectl get svc -n rate-limiter
kubectl get hpa -n rate-limiter
```

### 3. AWS Deployment (ECS + RDS + ElastiCache)

```
┌───────────────────────────────────────────────────────┐
│             AWS Infrastructure                        │
│                                                       │
│  ┌─────────────────────────────────────────────────┐ │
│  │  Application Load Balancer (ALB)                │ │
│  │  :80, :443                                      │ │
│  └────────────────────┬────────────────────────────┘ │
│                       │                               │
│  ┌────────────────────▼────────────────────────────┐ │
│  │  ECS Fargate Cluster                           │ │
│  │  ┌──────────────────────────────────────────┐  │ │
│  │  │ Service: rate-limiter-api                │  │ │
│  │  │ Task Count: 3 (auto-scaling: 3-10)       │  │ │
│  │  │ ┌──────────────────────────────────────┐│  │ │
│  │  │ │ Task 1: rate-limiter:latest          ││  │ │
│  │  │ │ vCPU: 0.5 | Memory: 1GB              ││  │ │
│  │  │ └──────────────────────────────────────┘│  │ │
│  │  │ ┌──────────────────────────────────────┐│  │ │
│  │  │ │ Task 2: rate-limiter:latest          ││  │ │
│  │  │ └──────────────────────────────────────┘│  │ │
│  │  │ ┌──────────────────────────────────────┐│  │ │
│  │  │ │ Task 3: rate-limiter:latest          ││  │ │
│  │  │ └──────────────────────────────────────┘│  │ │
│  │  └──────────────────────────────────────────┘  │ │
│  └──────────────────────────────────────────────────┘ │
│                                                       │
│  ┌──────────────────────────────────────────────────┐ │
│  │  Data Layer                                      │ │
│  │  ┌────────────────────────────────────────────┐ │ │
│  │  │ RDS PostgreSQL (Multi-AZ)                 │ │ │
│  │  │ db.r5.large                               │ │ │
│  │  │ ├─ Primary (us-east-1a)                  │ │ │
│  │  │ └─ Standby (us-east-1b)                  │ │ │
│  │  │ Backup: 30-day retention                  │ │ │
│  │  └────────────────────────────────────────────┘ │ │
│  │  ┌────────────────────────────────────────────┐ │ │
│  │  │ ElastiCache Redis Cluster                 │ │ │
│  │  │ cache.r6g.xlarge x 3 nodes                │ │ │
│  │  │ Cluster Mode: Enabled                      │ │ │
│  │  │ Auto Failover: Enabled                     │ │ │
│  │  └────────────────────────────────────────────┘ │ │
│  └──────────────────────────────────────────────────┘ │
│                                                       │
│  ┌──────────────────────────────────────────────────┐ │
│  │  Monitoring & Logging                           │ │
│  │  ├─ CloudWatch (logs, metrics)                  │ │
│  │  ├─ X-Ray (distributed tracing)                 │ │
│  │  └─ SNS (alerts)                                │ │
│  └──────────────────────────────────────────────────┘ │
└───────────────────────────────────────────────────────┘
```

**Deployment Steps:**

1. **Build & Push Docker Image**
   ```bash
   docker build -t rate-limiter:latest .
   aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account>.dkr.ecr.us-east-1.amazonaws.com
   docker tag rate-limiter:latest <account>.dkr.ecr.us-east-1.amazonaws.com/rate-limiter:latest
   docker push <account>.dkr.ecr.us-east-1.amazonaws.com/rate-limiter:latest
   ```

2. **Create RDS PostgreSQL Instance**
   ```bash
   aws rds create-db-instance \
     --db-instance-identifier ratelimiter-db \
     --db-instance-class db.r5.large \
     --engine postgres \
     --master-username admin \
     --master-user-password <secure-password> \
     --allocated-storage 100 \
     --multi-az
   ```

3. **Create ElastiCache Cluster**
   ```bash
   aws elasticache create-replication-group \
     --replication-group-description "Rate Limiter Cache" \
     --engine redis \
     --cache-node-type cache.r6g.xlarge \
     --num-cache-clusters 3 \
     --automatic-failover-enabled
   ```

4. **Create ECS Cluster & Service**
   ```bash
   # Use AWS CLI, CloudFormation, or Terraform
   # Define task definition with container image
   # Create service with ALB integration
   # Configure auto-scaling policies
   ```

## Scaling Strategies

### Vertical Scaling

```
Single Instance → Larger Instance

┌──────────────────────┐      ┌──────────────────────┐
│  t3.medium           │      │  c5.2xlarge          │
│  2 vCPU, 4GB RAM     │  →   │  8 vCPU, 16GB RAM    │
│  ~5K req/s           │      │  ~40K req/s          │
└──────────────────────┘      └──────────────────────┘

Pros:
• Simple to implement
• No code changes

Cons:
• Single point of failure
• Downtime during upgrade
• Cost inefficient at scale
```

### Horizontal Scaling

```
Multiple Instances → Distribute Load

       ┌─────────┐
       │   ALB   │
       └────┬────┘
     ┌──────┼──────┐
     │      │      │
  ┌──▼──┐ ┌─▼───┐ ┌──▼──┐
  │ API │ │ API │ │ API │  Each handles:
  │ :1  │ │ :2  │ │ :3  │  • 5-10K req/s
  └─────┘ └─────┘ └─────┘  • Automatic failover
              ▲              • Cost: N × single instance
              │
          Scales to 10+ instances

Pros:
• No single point of failure
• Automatic failover
• Cost efficient
• Can handle spikes

Cons:
• Requires load balancer
• More operational complexity
```

## Monitoring & Observability

### Key Metrics to Monitor

```
┌──────────────────────────────────────────┐
│ Metrics Dashboard                        │
├──────────────────────────────────────────┤
│                                          │
│ Application Metrics:                     │
│ ├─ Request Rate (req/s)                 │
│ ├─ Avg Latency (ms)                     │
│ ├─ P99 Latency (ms)                     │
│ ├─ Rate Limited Requests (%)            │
│ └─ Error Rate (%)                       │
│                                          │
│ Resource Metrics:                        │
│ ├─ CPU Usage (%)                        │
│ ├─ Memory Usage (%)                     │
│ ├─ Disk I/O (ops/s)                     │
│ └─ Network Throughput (Mbps)            │
│                                          │
│ Database Metrics:                        │
│ ├─ Connection Pool Usage                │
│ ├─ Query Latency (ms)                   │
│ ├─ Slow Queries                         │
│ └─ Replication Lag (ms)                 │
│                                          │
│ Cache Metrics:                           │
│ ├─ Hit Rate (%)                         │
│ ├─ Eviction Rate                        │
│ ├─ Memory Usage (%)                     │
│ └─ Latency (ms)                         │
│                                          │
│ Alerts Configured:                       │
│ • Latency > 100ms (p99)                 │
│ • Error Rate > 1%                       │
│ • CPU > 80%                             │
│ • Memory > 90%                          │
│ • Cache Hit Rate < 80%                  │
│ • Database connection pool full         │
└──────────────────────────────────────────┘
```

### Alerting Rules

| Condition | Severity | Action |
|-----------|----------|--------|
| P99 Latency > 100ms | Warning | Page on-call |
| Error Rate > 5% | Critical | Page + escalate |
| CPU > 90% | Warning | Auto-scale |
| Memory > 95% | Critical | Immediate investigation |
| Database down | Critical | Page all SRE |
| Cache hit rate < 50% | Warning | Investigate eviction |

## Disaster Recovery

### Backup Strategy

```
Database Backups:
• Automated: Daily snapshots (30-day retention)
• Manual: Before major updates
• Replication: Real-time to standby region
• Recovery: RTO < 1 hour, RPO < 5 minutes

Redis Backups:
• RDB snapshots: Hourly
• AOF (Append-Only File): Real-time
• Cluster redundancy: Data on 3+ nodes
• Recovery: RTO < 5 minutes

Configuration:
• Version control: All configs in Git
• Secrets: AWS Secrets Manager
• IaC: Terraform/CloudFormation
```

### Failover Process

1. **Automatic Failover**
   - Health checks detect failure
   - Router redirects to healthy instances
   - Database replicas promote
   - Cache cluster re-elects master

2. **Manual Failover** (if needed)
   ```bash
   # AWS RDS
   aws rds modify-db-instance --db-instance-identifier ratelimiter-db --apply-immediately

   # Kubernetes
   kubectl delete pod <failed-pod> -n rate-limiter
   kubectl scale deployment rate-limiter-api --replicas=4 -n rate-limiter
   ```

---

**Last Updated:** 2026-06-30
