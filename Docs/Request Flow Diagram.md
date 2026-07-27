# 🔄 Request Flow & Lifecycle Guide

## Overview

Every request sent to the API Gateway follows a structured processing pipeline before reaching downstream microservices or local router handlers.

Instead of directly executing business logic, incoming requests pass through a robust middleware stack responsible for **distributed trace correlation**, **structured logging**, **real-time metrics aggregation**, **dual-authentication**, and **atomic sliding window rate limiting**.

This layered architecture ensures separation of concerns, enterprise-grade security, high-throughput non-blocking performance, and complete system observability.

---

# Complete Request Lifecycle

```text
                               Client
                                 │
                                 │ HTTP Request (Bearer JWT / X-API-Key / X-Admin-Key)
                                 ▼
                     FastAPI API Gateway (Port 8000)
                                 │
                                 ▼
                    CorrelationIdMiddleware
                   (Injects/Tracks X-Request-ID)
                                 │
                                 ▼
                        LoggingMiddleware
                   (Single-line JSON Log Formatter)
                                 │
                                 ▼
                        MetricsMiddleware
                  (Aggregates hits/latency into Redis)
                                 │
                                 ▼
                   SlidingWindowRateLimiter
             ┌───────────────────┴───────────────────┐
             │                                       │
             ▼                                       ▼
    Authentication Check                    Rate Limit Evaluation
 (JWT Token or X-API-Key)                (Atomic Lua Script on Redis ZSET)
             │                                       │
      ┌──────┴──────┐                         ┌──────┴──────┐
      │             │                         │             │
      ▼             ▼                         ▼             ▼
   Valid         Invalid                   Allowed       Exceeded
      │             │                         │             │
      │             ▼                         │             ▼
      │          HTTP 401                     │          HTTP 429
      │        Unauthorized                   │      Too Many Requests
      │                                       │
      └───────────────────┬───────────────────┘
                          ▼
              Router & Reverse Proxy Layer
       ┌──────────────────┼──────────────────┐
       │                  │                  │
       ▼                  ▼                  ▼
 /auth Router      /admin Router      httpx Reverse Proxy
(Token Gen)       (Admin Analytics)   (/users & /products)
       │                  │                  │
       │                  │                  ▼
       │                  │        Downstream Microservice
       │                  │      (User: 8001 / Product: 8002)
       └──────────────────┼──────────────────┘
                          ▼
                 HTTP JSON Response
             (with Security Headers & X-Request-ID)
                          │
                          ▼
                        Client
```

---

# Step 1 – Client Sends Request

The process begins when a client (Browser, Swagger UI, Postman, or mobile client) issues an HTTP request.

### Example Request

```http
GET /users HTTP/1.1
Host: localhost:8000
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
X-Request-ID: c5f89e21-4d1a-4f81-a9b2-3e2b62d85409
```

Or using an API Key:

```http
GET /products HTTP/1.1
Host: localhost:8000
X-API-Key: a1b2c3d4e5f678901234567890abcdef
```

---

# Step 2 – Request Reaches Gateway & Pipeline Execution

The FastAPI application receives the request in `gateway/main.py`.

Execution pipeline order:

```text
1. CORSMiddleware ──▶ 2. SecurityHeaders ──▶ 3. SlidingWindowRateLimiter ──▶ 4. MetricsMiddleware ──▶ 5. LoggingMiddleware ──▶ 6. CorrelationIdMiddleware
```

---

# Step 3 – Correlation ID Injection

`CorrelationIdMiddleware` ensures distributed request tracing across the entire system.

Responsibilities:
- Reads `X-Request-ID` header from incoming request.
- If missing, generates a new UUID4 string.
- Attaches correlation ID to `request.state.correlation_id`.
- Forwards `X-Request-ID` to downstream microservices and response headers.

---

# Step 4 – Single-Line Structured JSON Logging

`LoggingMiddleware` captures execution timing and context.

Responsibilities:
- Measures total processing duration in milliseconds (`process_time`).
- Emits single-line JSON log containing method, path, status, duration, client IP, user agent, and correlation ID.
- Injects `X-Process-Time` response header.

### Example Log Output

```json
{
  "timestamp": "2026-07-28T03:45:12.123Z",
  "level": "INFO",
  "message": "HTTP GET /users 200 (2.45ms)",
  "extra_data": {
    "correlation_id": "c5f89e21-4d1a-4f81-a9b2-3e2b62d85409",
    "method": "GET",
    "path": "/users",
    "status_code": 200,
    "duration_ms": 2.45,
    "client_ip": "127.0.0.1",
    "user_agent": "Mozilla/5.0"
  }
}
```

---

# Step 5 – Real-time Metrics Aggregation

`MetricsMiddleware` records request stats into Redis without blocking request execution.

Responsibilities:
- Increments `metrics:total_requests` and adds duration to `metrics:total_duration_ms`.
- Tracks HTTP status codes (`2xx`, `4xx`, `429`, `5xx`).
- Increments per-endpoint hit counters (`metrics:endpoint:GET:/users`).
- Increments per-client usage counters (`metrics:client:<client_id>`).

---

# Step 6 – Dual Authentication & Rate Limit Evaluation

`SlidingWindowRateLimiter` enforces authentication, access control, and dynamic rate limits.

### 1. Public Endpoint Bypass
Public paths (`/`, `/health`, `/docs`, `/openapi.json`, `/auth/login`, `/admin/*`) bypass rate limiting.

### 2. Dual Authentication Verification
Checks client identity from:
- **Option A**: `X-API-Key` header verified via `APIKeyService`.
- **Option B**: `Authorization: Bearer <JWT>` verified via `jwt_handler.verify_token`.

If neither is valid:
```http
HTTP/1.1 401 Unauthorized
Content-Type: application/json

{
  "error": "Valid JWT Bearer token or X-API-Key is required"
}
```

### 3. Blacklist & Whitelist Evaluation
- **Blacklisted Clients**: Immediately returned `HTTP 403 Forbidden`.
- **Whitelisted Clients**: Bypasses rate limit checks directly to handler.

### 4. Dynamic Rate Limit Resolution
Determines client limit based on custom limit or role default:
- **Free**: 10 requests / 60 seconds
- **Premium**: 100 requests / 60 seconds
- **Admin**: 1,000,000 requests / 60 seconds

### 5. Atomic Redis Lua Script (`rate_limit.lua`)
Executes Lua script on Redis Sorted Set (`ZSET` at `sliding:<client>`):
1. Removes timestamps older than `(now - window)`.
2. Counts active requests in set via `ZCARD`.
3. If `count >= limit`, returns `0` (Denied).
4. Else, adds unique entry `tostring(now) .. ":" .. seq` via `ZADD`, sets TTL expire, and returns `1` (Allowed).

If limit is exceeded:
```http
HTTP/1.1 429 Too Many Requests
Retry-After: 60
X-RateLimit-Limit: 10
X-RateLimit-Remaining: 0
Content-Type: application/json

{
  "error": "Rate limit exceeded",
  "client": "bob",
  "limit": 10,
  "window": 60
}
```

---

# Step 7 – Router Layer & High-Performance Reverse Proxy

Once authentication and rate limiting succeed, the request reaches the target router:

### A. Auth Router (`/auth`)
- Handles user authentication (`POST /auth/login`) and issues signed JWT Access Tokens.

### B. Admin Router (`/admin`)
- Protected by `X-Admin-Key`.
- Manages client API keys, custom rate limits, role assignments, whitelisting/blacklisting, and real-time metrics (`GET /admin/metrics`).

### C. Microservice Reverse Proxy (`/users` & `/products`)
- `ProxyService` uses a singleton `httpx.AsyncClient` connection pool (`max_connections=200`).
- Forwards original request method, headers (with `X-Request-ID`), query params, and body to downstream services:
  - `/users` ──▶ `http://127.0.0.1:8001/users`
  - `/products` ──▶ `http://127.0.0.1:8002/products`
- **Error Handling**:
  - `httpx.TimeoutException` ──▶ `504 Gateway Timeout`
  - `httpx.RequestError` ──▶ `502 Bad Gateway`

---

# Step 8 – Response Returned with Security Headers

The response is passed back through the middleware stack:
1. `SecurityHeadersMiddleware` injects OWASP headers:
   - `X-Content-Type-Options: nosniff`
   - `X-Frame-Options: DENY`
   - `X-XSS-Protection: 1; mode=block`
   - `Strict-Transport-Security: max-age=31536000; includeSubDomains`
2. Rate limit headers attached:
   - `X-RateLimit-Limit: <limit>`
3. Correlation header attached:
   - `X-Request-ID: <uuid>`

### Example Successful Response

```http
HTTP/1.1 200 OK
Content-Type: application/json
X-Request-ID: c5f89e21-4d1a-4f81-a9b2-3e2b62d85409
X-Process-Time: 2.45ms
X-RateLimit-Limit: 10
X-Content-Type-Options: nosniff
X-Frame-Options: DENY

{
  "service": "User Service",
  "count": 3,
  "users": [
    { "id": "1", "username": "shubham", "email": "shubham@example.com", "role": "admin" },
    { "id": "2", "username": "alice", "email": "alice@example.com", "role": "premium" },
    { "id": "3", "username": "bob", "email": "bob@example.com", "role": "free" }
  ]
}
```

---

# Summary of Pipeline Advantages

- **Zero Race Conditions**: Atomic Lua script executes in a single Redis round-trip.
- **Non-Blocking Performance**: Built with `redis.asyncio` and `httpx` async connection pools.
- **End-to-End Traceability**: Injected `X-Request-ID` correlates logs across Gateway and microservices.
- **Dual Security Model**: Native support for both Bearer JWT and X-API-Key authentication.
- **Full Observability**: Real-time aggregated metrics and Redis stats accessible at `/admin/metrics`.