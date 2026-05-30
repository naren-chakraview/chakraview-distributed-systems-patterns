# Local Development Environment

Quick-start guide for running the distributed systems patterns reference implementation locally with full observability.

## Prerequisites

- Docker and Docker Compose (v2.0+)
- Python 3.10+
- Git

## Quick Start

### 1. Start Services

```bash
cd examples/local-dev
docker-compose up -d
```

### 2. Verify Services

```bash
# Check all services are healthy
docker-compose ps

# Verify PostgreSQL
docker-compose exec postgres pg_isready -U agents_user

# Verify Redis
docker-compose exec redis redis-cli ping

# Verify RabbitMQ
docker-compose exec queue rabbitmq-diagnostics ping

# Verify Jaeger UI
open http://localhost:16686
```

### 3. Run Tests

```bash
cd ../..
pytest tests/integration/test_full_pipeline.py -v
```

### 4. Run Demo Scripts

```bash
python examples/pattern-demos/demo_token_budgeting.py
python examples/pattern-demos/demo_causality.py
python examples/pattern-demos/demo_tracing.py
```

## Services Overview

### PostgreSQL (Port 5432)
- **Purpose**: Persistent state storage
- **Database**: `agents_db`
- **User**: `agents_user`
- **Password**: `agents_password`
- **Usage**: Store transaction data, customer profiles, agent decisions

**Connection String:**
```
postgresql://agents_user:agents_password@localhost:5432/agents_db
```

**Sample Tables:**
```sql
-- Transactions
CREATE TABLE transactions (
    id SERIAL PRIMARY KEY,
    transaction_id UUID UNIQUE,
    amount DECIMAL(10,2),
    merchant VARCHAR(255),
    location VARCHAR(100),
    fraud_risk_score FLOAT,
    timestamp TIMESTAMP
);

-- Customer Segments
CREATE TABLE customer_segments (
    id SERIAL PRIMARY KEY,
    customer_id UUID UNIQUE,
    segment VARCHAR(50),
    confidence FLOAT,
    updated_at TIMESTAMP
);

-- Agent Metrics
CREATE TABLE agent_metrics (
    id SERIAL PRIMARY KEY,
    agent_id VARCHAR(100),
    metric_name VARCHAR(100),
    metric_value FLOAT,
    timestamp TIMESTAMP
);
```

### Redis (Port 6379)
- **Purpose**: High-speed caching and session storage
- **Usage**: Cache agent decisions, customer segment assignments, fraud scores

**Sample Commands:**
```bash
# Connect to Redis
docker-compose exec redis redis-cli

# Set cache entry
SET agent:intent:msg123 '{"intent":"purchase","confidence":0.85}'

# Get cached decision
GET agent:intent:msg123

# Set expiration (1 hour)
EXPIRE agent:intent:msg123 3600
```

### Jaeger (Port 16686 for UI, 6831 for agent SDK)
- **Purpose**: Distributed tracing and observability
- **UI**: http://localhost:16686
- **Usage**: Trace requests across agents, debug latency issues

**Using from Agents:**
```python
from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter

jaeger_exporter = JaegerExporter(
    agent_host_name="localhost",
    agent_port=6831,
)

tracer = trace.get_tracer(__name__)

with tracer.start_as_current_span("agent_execution") as span:
    span.set_attribute("agent_id", "intent-edge-1")
    span.set_attribute("input_tokens", 100)
    # Execute agent logic
```

### RabbitMQ (Port 5672 for AMQP, 15672 for UI)
- **Purpose**: Async message queue for agent coordination
- **UI**: http://localhost:15672 (guest/guest or agents_user/agents_password)
- **Usage**: Queue messages between agents, enable async processing

**Publishing Messages:**
```python
import pika

connection = pika.BlockingConnection(
    pika.ConnectionParameters(
        host='localhost',
        credentials=pika.PlainCredentials('agents_user', 'agents_password')
    )
)
channel = connection.channel()

# Declare queue
channel.queue_declare(queue='agent_decisions', durable=True)

# Publish message
channel.basic_publish(
    exchange='',
    routing_key='agent_decisions',
    body=json.dumps({
        'trace_id': 'trace_abc123',
        'intent': 'purchase',
        'confidence': 0.85
    })
)
```

### Prometheus (Port 9090)
- **Purpose**: Metrics collection and time-series storage
- **UI**: http://localhost:9090
- **Usage**: Query agent metrics (token consumption, latency, error rates)

**Sample Queries:**
```promql
# Token consumption rate
rate(agent_tokens_consumed_total[5m])

# Agent latency p99
histogram_quantile(0.99, rate(agent_latency_seconds_bucket[5m]))

# Error rate
rate(agent_errors_total[5m])
```

### Grafana (Port 3000)
- **Purpose**: Metrics visualization and dashboards
- **UI**: http://localhost:3000
- **Default Login**: admin / agents_password
- **Usage**: View pre-built dashboards for agent health

## Common Tasks

### View Agent Trace

1. Open Jaeger UI: http://localhost:16686
2. Select "service" dropdown → choose agent service
3. Click "Find Traces"
4. Click on a trace to see full causal flow

### Query Agent Decisions from Database

```bash
docker-compose exec postgres psql -U agents_user -d agents_db

# In psql:
SELECT * FROM agent_decisions
WHERE agent_id = 'intent-edge-1'
ORDER BY timestamp DESC
LIMIT 10;
```

### Monitor Message Queue

1. Open RabbitMQ UI: http://localhost:15672
2. Login with: agents_user / agents_password
3. Check queues in "Queues" tab
4. View message rates and depths

### Check Redis Cache Hit Rate

```bash
docker-compose exec redis redis-cli INFO stats

# Look for:
# keyspace_hits: number of successful reads
# keyspace_misses: number of cache misses
# Hit rate = hits / (hits + misses)
```

## Cleanup

### Stop All Services

```bash
docker-compose down
```

### Remove All Data (WARNING: destructive)

```bash
docker-compose down -v
```

This removes all volumes including databases.

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f postgres

# Filter by agent startup
docker-compose logs postgres | grep agent
```

## Environment Variables

Customize services by editing `docker-compose.yml`:

- **POSTGRES_PASSWORD**: Change database password
- **RABBITMQ_DEFAULT_PASS**: Change queue password
- **GF_SECURITY_ADMIN_PASSWORD**: Change Grafana admin password

## Troubleshooting

### Port Already in Use

```bash
# Find what's using port 5432
lsof -i :5432

# Kill process
kill -9 <PID>

# Or change port in docker-compose.yml
# Change "5432:5432" to "15432:5432"
```

### Service Health Check Failed

```bash
# View logs for specific service
docker-compose logs postgres

# Restart service
docker-compose restart postgres
```

### Can't Connect to Database

```bash
# Verify connection parameters
docker-compose exec postgres psql -U agents_user -d agents_db

# If psql not found, install postgres client:
# macOS: brew install libpq
# Ubuntu: sudo apt install postgresql-client
```

### Out of Memory

Docker compose uses significant resources. Increase Docker desktop memory:
- macOS: Docker Desktop → Preferences → Resources → Memory (recommend 8GB+)
- Linux: Check available memory with `free -h`

## Next Steps

1. **Run integration tests** to verify all services work
2. **Read documentation** in `docs/patterns/` to understand each pattern
3. **Run demo scripts** to see patterns in action
4. **Inspect Jaeger traces** to see distributed tracing
5. **Check Grafana dashboards** to monitor agent metrics

See the main [README.md](../../README.md) for pattern documentation.
