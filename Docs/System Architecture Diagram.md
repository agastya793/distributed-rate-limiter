## 🏗️ System Architecture

```text
                                     ┌────────────────────────────────────────────────────────┐
                                     │            Client / Swagger UI / Postman               │
                                     └───────────────────────────┬────────────────────────────┘
                                                                 │ HTTP Request (Bearer JWT / X-API-Key / X-Admin-Key)
                                                                 ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                                 FASTAPI API GATEWAY (Port 8000)                                              │
│                                                                                                                             │
│  ┌───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐  │
│  │                                                   MIDDLEWARE PIPELINE                                                │  │
│  │                                                                                                                       │  │
│  │  1. CorrelationIdMiddleware   ──▶ Injects / passes unique `X-Request-ID` across logs & microservices                 │  │
│  │  2. LoggingMiddleware          ──▶ Emits structured single-line JSON logs (Latency, Path, Status, Request-ID, Client IP)│  │
│  │  3. MetricsMiddleware          ──▶ Aggregates request counts, endpoint hit stats, status codes, and latency into Redis   │  │
│  │  4. SlidingWindowRateLimiter   ──▶ Enforces Dual Auth (JWT/API-Key), Whitelist/Blacklist & executes Lua script on Redis│  │
│  │  5. SecurityHeadersMiddleware ──▶ Injects OWASP response security headers (nosniff, DENY, HSTS, XSS protection)       │  │
│  └───────────────────────────────────────────────────────────┬───────────────────────────────────────────────────────────┘  │
│                                                              │                                                              │
│  ┌───────────────────────────────────────────────────────────┴───────────────────────────────────────────────────────────┐  │
│  │                                                     ROUTER LAYER                                                     │  │
│  │                                                                                                                       │  │
│  │   ├── /auth   ──▶ Token generation & user login (`/auth/login`)                                                      │  │
│  │   ├── /admin  ──▶ Protected endpoints (API keys, dynamic rate limits, role policies, metrics analytics)              │  │
│  │   ├── /users  ──▶ Reverse Proxy Engine (`httpx` connection pool ──▶ User Microservice)                                 │  │
│  │   └── /products──▶ Reverse Proxy Engine (`httpx` connection pool ──▶ Product Microservice)                              │  │
│  └───────────────────────────────────────────────────────────┬───────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────┼──────────────────────────────────────────────────────────────┘
                                                               │
                                  ┌────────────────────────────┼────────────────────────────┐
                                  ▼                            ▼                            ▼
                      ┌──────────────────────┐     ┌──────────────────────┐     ┌──────────────────────┐
                      │    Redis Service     │     │     User Service     │     │   Product Service    │
                      │   (redis.asyncio)    │     │   (FastAPI - 8001)   │     │   (FastAPI - 8002)   │
                      │     (Port 6379)      │     │  (User DB Microservice)│     │(Product DB Microservice)│
                      └──────────────────────┘     └──────────────────────┘     └──────────────────────┘
```

---

### 🧩 Component Breakdown

| Component | Class / Service | Purpose |
| :--- | :--- | :--- |
| **API Gateway** | `FastAPI (main.py)` | Single entry point on Port 8000 handling routing, security, reverse proxying, and global lifecycle management. |
| **Correlation ID Tracking** | `CorrelationIdMiddleware` | Generates or forwards a unique `X-Request-ID` across every log line and downstream microservice request for distributed tracing. |
| **Structured JSON Logging** | `LoggingMiddleware` | Formats and outputs single-line JSON logs with method, path, HTTP status, execution latency (ms), client IP, and correlation ID. |
| **Real-time Metrics Collector** | `MetricsMiddleware` & `MetricsService` | Asynchronously records request counts, endpoint hit statistics, status codes (2xx, 4xx, 429, 5xx), average latency, and Redis health. |
| **Sliding Window Rate Limiter** | `SlidingWindowRateLimiter` | Evaluates dynamic client limits, role-based policies (Free: 10/m, Premium: 100/m, Admin: 1M/m), whitelists, blacklists, and atomic Redis Lua scripts. |
| **Security Headers** | `SecurityHeadersMiddleware` | Injects OWASP standard response headers (`X-Content-Type-Options`, `X-Frame-Options`, `HSTS`, `XSS Protection`). |
| **Dual Authentication** | `JWTHandler` & `APIKeyService` | Verifies identity via either **JWT Bearer Tokens** (`/auth/login`) or **Client X-API-Key Headers**. |
| **Admin Management API** | `gateway/routers/admin.py` | Protected by `X-Admin-Key` header; enables dynamic rate-limiting overrides, API Key creation/revocation, client role assignment, and live `/admin/metrics`. |
| **Async Reverse Proxy Engine** | `ProxyService (httpx)` | High-performance reverse proxy using an `httpx.AsyncClient` connection pool (`max_connections=200`) with `502 Bad Gateway` and `504 Gateway Timeout` error handling. |
| **Redis Store & Atomic Engine**| `RedisService & rate_limit.lua` | Non-blocking `redis.asyncio` store running an atomic Lua script (`ZSET`) to drop expired timestamps and record requests in 1 round-trip. |
| **Downstream Microservices** | `User Service (8001)` & `Product Service (8002)` | Isolated downstream FastAPI backend microservices handling domain-specific business logic. |
