# 🚀 Production-Inspired API Gateway & Distributed Rate Limiter

A production-grade, distributed **API Gateway & Microservice Architecture** built using **FastAPI**, **Redis (`redis.asyncio`)**, **Lua Scripting**, **JWT Authentication**, and **Docker Compose**. 

This system demonstrates real-world backend engineering concepts beyond standard CRUD applications, featuring distributed sliding window rate limiting, high-performance async reverse proxying, correlation ID tracing, structured JSON logging, dynamic rate limit policy overrides, and comprehensive observability.

---

## 📌 Architecture Overview

```
                                     ┌────────────────────────────────────────────────────────┐
                                     │               Client / Swagger UI / Postman            │
                                     └───────────────────────────┬────────────────────────────┘
                                                                 │ HTTP Request (Bearer JWT / X-API-Key)
                                                                 ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                                 FASTAPI API GATEWAY (Port 8000)                                              │
│                                                                                                                             │
│  ┌───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐  │
│  │                                                   MIDDLEWARE PIPELINE                                                │  │
│  │                                                                                                                       │  │
│  │  1. CorrelationIdMiddleware   ──▶ Generates / injects unique `X-Request-ID` for distributed tracing                  │  │
│  │  2. StructuredLoggingMiddleware ──▶ Emits single-line JSON logs (Timestamp, Latency, Path, Status, Request-ID)         │  │
│  │  3. MetricsMiddleware          ──▶ Asynchronously records request counts, status codes, and latency histograms into Redis│  │
│  │  4. SlidingWindowRateLimiter   ──▶ Evaluates Whitelist/Blacklist & executes Atomic Lua script on Redis sorted set     │  │
│  └───────────────────────────────────────────────────────────┬───────────────────────────────────────────────────────────┘  │
│                                                              │                                                              │
│  ┌───────────────────────────────────────────────────────────┴───────────────────────────────────────────────────────────┐  │
│  │                                                     ROUTER LAYER                                                     │  │
│  │                                                                                                                       │  │
│  │   ├── /auth   ──▶ Token generation & client authentication                                                           │  │
│  │   ├── /admin  ──▶ Protected management endpoints (API keys, custom rate limits, roles, metrics analytics)            │  │
│  │   ├── /users  ──▶ High-Performance Reverse Proxy Service (httpx connection pool ──▶ User Service)                     │  │
│  │   └── /products──▶ High-Performance Reverse Proxy Service (httpx connection pool ──▶ Product Service)                  │  │
│  └───────────────────────────────────────────────────────────┬───────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────┼──────────────────────────────────────────────────────────────┘
                                                               │
                                  ┌────────────────────────────┼────────────────────────────┐
                                  ▼                            ▼                            ▼
                      ┌──────────────────────┐     ┌──────────────────────┐     ┌──────────────────────┐
                      │    Redis Service     │     │     User Service     │     │   Product Service    │
                      │   (redis.asyncio)    │     │   (FastAPI - 8001)   │     │   (FastAPI - 8002)   │
                      └──────────────────────┘     └──────────────────────┘     └──────────────────────┘
```

---

## ⚡ Core Features & Engineering Highlights

- ⚡ **Atomic Distributed Sliding Window Rate Limiting**: Implemented using **Redis Sorted Sets (`ZSET`)** and executed via an **atomic Lua script (`rate_limit.lua`)** in a single non-blocking network round-trip.
- 🔄 **Async I/O & Connection Pooling**: Utilizes `redis.asyncio` and `httpx.AsyncClient` singleton connection pools (`Limits(max_keepalive_connections=50, max_connections=200)`) preventing event loop blocking and socket exhaustion.
- 🔀 **High-Performance Reverse Proxy**: Proxies requests, headers, query parameters, request bodies, and response status codes seamlessly to downstream microservices with `502 Bad Gateway` and `504 Gateway Timeout` error handling.
- 🆔 **Distributed Trace Tracking**: Injects and context-tracks `X-Request-ID` across every log line and downstream proxy header.
- 🔑 **Dual Security Architecture**: Native OpenAPI / Swagger UI support for both **JWT Bearer tokens** and **X-API-Key headers**.
- 🛡️ **Role & Client Policy Management**: Dynamic custom rate limit overrides per client (`rate_limit:<client>`), role-based defaults (Free: 10/min, Premium: 100/min, Admin: 1M/min), whitelisting, and blacklisting.
- 📊 **Real-time Observability**: Collects endpoint hit counts, client usage stats, latency totals, rate limit blocks, and Redis memory statistics via `/admin/metrics`.
- 📦 **Multi-Container Docker Compose**: Full orchestration of Gateway, Redis, User Service, and Product Service with container health checks.
- 🧪 **Automated Testing Suite**: Built with `pytest` and `httpx.AsyncClient` covering health checks, auth token verification, admin policies, and middleware pipelines.

---

## 📂 Project Structure

```text
distributed-rate-limiter/
├── gateway/
│   ├── auth/
│   │   ├── api_key.py              # X-API-Key validation dependency
│   │   ├── dependencies.py         # HTTPBearer & dual-auth client dependencies
│   │   └── jwt_handler.py          # JWT creation and decoding helpers
│   ├── core/
│   │   ├── config.py               # Centralized typed Settings configuration
│   │   └── logging_config.py        # Structured JSON log formatter
│   ├── exceptions/
│   │   └── handlers.py             # Global exception handlers
│   ├── middleware/
│   │   ├── correlation.py          # X-Request-ID trace injection middleware
│   │   ├── logging.py              # Structured JSON request timing middleware
│   │   ├── metrics_middleware.py   # Asynchronous metrics recording middleware
│   │   ├── security_headers.py     # OWASP response security headers middleware
│   │   └── sliding_window.py       # Atomic Lua-backed rate limiter middleware
│   ├── models/
│   │   └── admin.py                # Admin API Pydantic schemas
│   ├── routers/
│   │   ├── admin.py                # Admin endpoints (protected by X-Admin-Key)
│   │   ├── auth.py                 # Authentication endpoints (/auth/login)
│   │   ├── product.py              # Reverse proxy router for Product Service
│   │   └── user.py                 # Reverse proxy router for User Service
│   ├── scripts/
│   │   └── rate_limit.lua          # Atomic Redis sliding window Lua script
│   ├── services/
│   │   ├── api_key_service.py      # Async Redis API key storage & validation
│   │   ├── metrics_service.py      # Real-time metrics aggregator & analytics
│   │   ├── proxy_service.py        # Async httpx reverse proxy engine
│   │   ├── redis_service.py        # Non-blocking redis.asyncio pool manager
│   │   └── user_limit_service.py   # Client limits, roles, whitelist & blacklist service
│   ├── tests/
│   │   ├── conftest.py             # Pytest fixtures & AsyncClient setup
│   │   ├── test_admin.py           # Admin endpoint integration tests
│   │   ├── test_auth.py            # Authentication & JWT unit tests
│   │   ├── test_health.py          # Gateway healthcheck unit tests
│   │   └── test_proxy.py           # Reverse proxy, dual auth & rate limiting integration tests
│   └── main.py                     # FastAPI main application & middleware registration
├── services/
│   ├── user_service/
│   │   ├── Dockerfile              # Standalone User Service container build
│   │   └── main.py                 # User Microservice FastAPI application (Port 8001)
│   └── product_service/
│       ├── Dockerfile              # Standalone Product Service container build
│       └── main.py                 # Product Microservice FastAPI application (Port 8002)
├── Docs/                           # Deep-dive architecture and component documentation
│   ├── API EndPoint Table.md       # Categorized API reference table
│   ├── deployment.md               # Detailed local & Docker deployment guide
│   ├── detail-authentication.md    # Dual JWT & X-API-Key security guide
│   ├── Redis Data Flow.md          # Atomic Lua script & Redis key schema
│   ├── Request Flow Diagram.md     # Request lifecycle & middleware pipeline
│   └── System Architecture Diagram.md # Complete ASCII architecture & component breakdown
├── docker-compose.yml              # Production multi-container orchestration
├── Dockerfile                      # Gateway container build
├── requirements.txt                # Python dependencies manifest
└── README.md                       # System documentation & architectural showcase
```

---

## ⚙️ Quickstart Guide

### Option A: Running with Docker Compose (Recommended)

Boot all 4 containers (`redis`, `gateway`, `user-service`, `product-service`) in single-command orchestration:

```bash
docker compose up --build
```

Access services:
- **Gateway Swagger UI**: `http://localhost:8000/docs`
- **Gateway Health Check**: `http://localhost:8000/health`
- **User Service (Direct)**: `http://localhost:8001/users`
- **Product Service (Direct)**: `http://localhost:8002/products`

---

### Option B: Local Python Development

#### 1. Clone & Setup Virtual Environment
```bash
git clone <repository-url>
cd distributed-rate-limiter
python -m venv venv
venv\Scripts\activate   # Windows
# source venv/bin/activate # Linux/macOS
pip install -r requirements.txt
```

#### 2. Start Services
Ensure local Redis is running on port `6379`.

Start microservices:
```bash
# Terminal 1: User Service
python -m uvicorn services.user_service.main:app --port 8001

# Terminal 2: Product Service
python -m uvicorn services.product_service.main:app --port 8002

# Terminal 3: API Gateway
python -m uvicorn gateway.main:app --port 8000 --reload
```

---

## 🧪 Running Automated Tests

Run the complete test suite using `pytest`:

```bash
python -m pytest gateway/tests/ -v
```

Expected output:
```text
============================= test session starts =============================
collected 11 items

gateway/tests/test_admin.py PASSED                                     [ 25%]
gateway/tests/test_auth.py PASSED                                      [ 50%]
gateway/tests/test_health.py PASSED                                     [ 75%]
gateway/tests/test_proxy.py PASSED                                      [100%]

============================= 11 passed in 0.35s ==============================
```

---

## 📡 API Reference & Live Web Dashboard

- 🎨 **Web Dashboard UI**: `/dashboard` (Interactive Glassmorphism Dashboard)
- 📜 **Swagger UI API Docs**: `/docs` (Interactive OpenAPI 3.1.0 Specification)

### Authentication
- `POST /auth/login`: Generate JWT Access Token.

### Microservice Reverse Proxy Routes
- `GET /users`: Proxied to User Service (`http://user-service:8001/users`).
- `GET /users/{id}`: Proxied to User Service (`http://user-service:8001/users/{id}`).
- `GET /products`: Proxied to Product Service (`http://product-service:8002/products`).
- `GET /products/{id}`: Proxied to Product Service (`http://product-service:8002/products/{id}`).

### Protected Admin Management (Requires Header: `X-Admin-Key: admin-secret-key-12345`)
- `POST /admin/api-key/{client}`: Generate API Key for a client.
- `DELETE /admin/api-key/{api_key}`: Revoke an API Key.
- `POST /admin/rate-limit`: Set custom rate limit for a client.
- `GET /admin/rate-limits`: Retrieve custom rate limits.
- `POST /admin/role`: Assign client role (`free`, `premium`, `admin`).
- `POST /admin/whitelist/{client}`: Whitelist a client (bypasses rate limit).
- `POST /admin/blacklist/{client}`: Blacklist a client (returns HTTP 403).
- `GET /admin/metrics`: Fetch real-time analytics summary, endpoint hits, and Redis operational stats.

---

## 👨‍💻 Author

**Shubham Thakur**  
*Backend Engineer | FastAPI | Python | Redis | Distributed Systems*
