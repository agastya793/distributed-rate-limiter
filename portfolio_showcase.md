# 🎓 API Gateway & Distributed Rate Limiter: Portfolio & Interview Guide

---

## 📄 Resume Bullet Points (Tailored for Recruiters & Hiring Managers)

### Option A: Senior Backend / Distributed Systems Engineer Format
- **Architected and built a high-throughput API Gateway in FastAPI and Redis**, handling distributed rate limiting, JWT/API Key authentication, and reverse proxying across microservices.
- **Eliminated race conditions and network overhead** by implementing an atomic Redis sliding window rate-limiting algorithm using Lua scripts (`ZSET`), reducing Redis round-trips from 4 to 1 per request.
- **Implemented non-blocking async architecture using `redis.asyncio` and `httpx.AsyncClient` connection pools** (`max_connections=200`), eliminating event loop stalls and supporting high-concurrency requests.
- **Designed a single-responsibility middleware pipeline** comprising Correlation ID tracking (`X-Request-ID`), structured single-line JSON logging, real-time metrics aggregation, OWASP security headers, and rate limiting.
- **Orchestrated multi-service microservice deployment** using Docker Compose across 4 containerized services with health checks and bridge network isolation.
- **Authored automated test suite (`pytest`, `httpx.AsyncClient`)** achieving 100% pass rate across authentication, rate limiting policy enforcement, admin endpoints, and middleware chains.

---

## 🎯 Recruiter & Technical Pitch (Elevator Pitch)

> *"This project isn't a typical CRUD app—it's a production-style API Gateway that sits in front of downstream microservices. I built it to demonstrate core backend engineering concepts like distributed sliding window rate limiting backed by Redis and atomic Lua scripts, non-blocking async I/O connection pooling, dual authentication (JWT + API Keys), structured JSON logging with correlation trace IDs, and multi-container Docker orchestration. It showcases how real-world enterprise gateways handle traffic control, security, and observability at scale."*

---

## 🧠 Technical Interview Questions & Answers

### Q1: Why did you use Redis Sorted Sets (`ZSET`) and Lua scripts for the Sliding Window Rate Limiter?
**Answer**: 
> *"A fixed-window rate limiter suffers from boundary burst issues—where a client sends double their limit at the edge of a window. A sliding window tracks exact request timestamps. We use Redis Sorted Sets (`ZSET`) where the key is the client ID, the score is the timestamp, and the value is the unique request ID/timestamp.*
> 
> *Without a Lua script, calculating the sliding window requires 4 separate Redis commands: `ZREMRANGEBYSCORE` to drop expired entries, `ZCARD` to count remaining requests, `ZADD` to add the new timestamp, and `EXPIRE` to refresh the TTL. Executing these separately causes race conditions under high concurrency and adds network latency.*
> 
> *By executing these operations inside an atomic Lua script (`rate_limit.lua`), Redis executes all commands in a single thread without interruption, guaranteeing atomicity and reducing network I/O from 4 round-trips to 1."*

---

### Q2: How did you ensure the FastAPI Gateway does not block the async event loop under heavy traffic?
**Answer**:
> *"FastAPI runs on a single-threaded async event loop (`uvicorn`/`anyio`). Any synchronous blocking call—such as traditional `redis-py` calls or `time.sleep()`—stalls the entire event loop for all concurrent users.*
> 
> *To prevent this, I migrated all Redis interactions to `redis.asyncio` with connection pooling (`max_connections=20`). For the reverse proxy, I created a long-lived `httpx.AsyncClient` singleton pool rather than creating a new HTTP client per request. This ensures all network I/O is non-blocking and pooled, enabling the gateway to handle thousands of concurrent requests smoothly."*

---

### Q3: How does the Gateway handle downstream service failures in the Reverse Proxy?
**Answer**:
> *"The `ProxyService` wraps outgoing requests to downstream microservices inside async try-except blocks catching `httpx.TimeoutException` and `httpx.RequestError`.*
> 
> *If a downstream service takes longer than the configured timeout (30s timeout, 5s connect timeout), the gateway catches `TimeoutException` and immediately returns a standard `504 Gateway Timeout` JSON response. If a downstream service is down or unreachable, the gateway catches `RequestError` and returns a clean `502 Bad Gateway` response, preventing unhandled server crashes and informing the client accurately."*

---

### Q4: How is request tracing handled across microservices?
**Answer**:
> *"Every incoming request passes through the `CorrelationIdMiddleware` at the very top of the middleware stack. It checks for an incoming `X-Request-ID` header; if missing, it generates a unique UUID4 and attaches it to `request.state.correlation_id`.*
> 
> *This ID is automatically passed downstream in `httpx` proxy headers, logged in every single-line JSON log emitted by `LoggingMiddleware`, and included in response headers. This allows developers to trace a single request end-to-end across Gateway logs, User Service logs, and Product Service logs."*

---

## 🗺️ System Design & Architectural Deep Dive

### 1. Sliding Window Algorithm Mechanics
```text
  Window = 60 Seconds | Limit = 5 Requests
  
  Timeline (Seconds):
  [ Now - 60s ] ──────────────────────────────────────────────▶ [ Now ]
       │                                                         │
       │-- Remove entries with timestamp < (Now - 60s)           │-- Count ZCARD(key)
       │   via ZREMRANGEBYSCORE                                  │   If ZCARD >= Limit ──▶ Deny (429)
                                                                 │   Else ZADD(key, Now, Now) ──▶ Allow (200)
```

---

## 🔮 Version 2 Roadmap & Future Enhancements

1. **Distributed Dynamic Configuration**:
   - Integrate HashiCorp Consul or Redis Pub/Sub to push rate limit policy updates dynamically to Gateway nodes without zero-downtime restarts.
2. **Prometheus & Grafana Dashboard**:
   - Expose standard Prometheus `/metrics` endpoint using `prometheus_client` and construct Grafana dashboards for latency distribution percentiles (p50, p90, p99).
3. **Circuit Breaker Pattern**:
   - Implement `pybreaker` or custom sliding-window circuit breaker state machine (Closed, Open, Half-Open) to fail-fast when downstream microservices degrade.
4. **gRPC Protocol Support**:
   - Support high-performance binary gRPC routing and HTTP/JSON to gRPC transcoding for internal microservice communication.
