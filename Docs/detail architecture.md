# 🏗️ System Architecture

## Overview

The **Distributed Rate Limiter API Gateway** is designed using a modular backend architecture where each component has a single responsibility. The gateway acts as the entry point for every client request and coordinates authentication, request logging, rate limiting, and route execution before sending a response back to the client.

This architecture follows the principle of **Separation of Concerns (SoC)**, making the application easier to maintain, test, and extend.

---

# High-Level Architecture

```text
                           Client
                              │
                              │ HTTP Request
                              ▼
                 ┌─────────────────────────┐
                 │    FastAPI Gateway      │
                 └─────────────────────────┘
                              │
             ┌────────────────┼────────────────┐
             ▼                ▼                ▼
     Logging Middleware  Sliding Window    Authentication
                           Rate Limiter        (JWT)
             │                │                │
             └────────────────┼────────────────┘
                              ▼
                        Route Handler
                              │
                              ▼
                           Redis
                              │
                              ▼
                      JSON API Response
```

---

# Request Lifecycle

Every request follows the same processing pipeline.

```text
Client
   │
   ▼
FastAPI Gateway
   │
   ▼
Logging Middleware
   │
   ▼
Sliding Window Rate Limiter
   │
   ▼
JWT Authentication (Protected Routes)
   │
   ▼
Route Handler
   │
   ▼
Business Logic
   │
   ▼
JSON Response
```

---

# Component Responsibilities

## 1. FastAPI Gateway

The gateway is the central entry point of the application.

Responsibilities:

- Receives incoming HTTP requests
- Registers API routes
- Loads middleware
- Handles application startup
- Returns HTTP responses

File

```
gateway/main.py
```

---

## 2. Logging Middleware

Every incoming request passes through the logging middleware before reaching any endpoint.

Responsibilities

- Record HTTP method
- Record request path
- Measure processing time
- Print request logs

Example

```text
GET /users
200 OK
Processing Time: 4.8 ms
```

File

```
gateway/middleware/logging.py
```

---

## 3. Sliding Window Rate Limiter

The rate limiter prevents clients from overwhelming the API with excessive requests.

Responsibilities

- Track request timestamps
- Remove expired timestamps
- Count active requests
- Reject requests exceeding the configured limit

Current Configuration

```
Requests : 5
Window   : 60 Seconds
```

File

```
gateway/middleware/sliding_window.py
```

---

## 4. Redis

Redis stores request timestamps for the sliding window algorithm.

Instead of storing request counts in application memory, Redis provides:

- Fast in-memory storage
- Automatic expiration
- Efficient sorted-set operations
- Shared state across application instances

Current Redis Data

```text
Key

sliding:127.0.0.1

↓

Sorted Set

↓

Timestamp
Timestamp
Timestamp
Timestamp
```

---

## 5. Authentication

JWT authentication protects private API endpoints.

Responsibilities

- Generate JWT
- Verify JWT
- Reject invalid tokens
- Return authenticated user information

Files

```
gateway/auth/jwt_handler.py

gateway/auth/dependencies.py
```

---

## 6. Routers

Routers separate API endpoints according to their functionality.

Example

```text
Authentication

↓

/auth/login

Users

↓

/users

Products

↓

/products
```

This keeps the application modular and easy to maintain.

---

## 7. Configuration

Application configuration is centralized using environment variables.

Configuration includes:

- Redis Host
- Redis Port
- JWT Secret
- JWT Algorithm
- Token Expiration
- Rate Limit
- Time Window

File

```
gateway/core/config.py
```

---

# Folder Organization

```text
gateway/
│
├── auth/
│
├── core/
│
├── middleware/
│
├── routers/
│
├── services/
│
├── exceptions/
│
└── main.py
```

Every folder is responsible for exactly one part of the application.

---

# Design Principles

This project follows several software engineering principles.

## Separation of Concerns

Each module performs one specific task.

Examples

- Authentication
- Logging
- Rate Limiting
- Routing

---

## Modularity

Every feature is implemented independently.

For example, replacing JWT with OAuth would only require changes inside the authentication module.

---

## Configuration Management

Application settings are loaded from the `.env` file instead of being hardcoded.

Benefits

- Easier deployment
- Environment-specific configuration
- Improved security

---

## Middleware-Based Processing

Cross-cutting concerns such as logging and rate limiting are handled through middleware instead of individual route handlers.

This keeps business logic clean and reusable.

---

# Technology Stack

| Technology | Purpose |
|------------|---------|
| FastAPI | API Gateway |
| Python | Backend Language |
| Redis | Sliding Window Storage |
| JWT | Authentication |
| Uvicorn | ASGI Server |
| dotenv | Environment Configuration |

---

# Future Improvements

The current architecture can be extended with:

- Docker
- Docker Compose
- Reverse Proxy
- Prometheus Monitoring
- Grafana Dashboard
- Role-Based Access Control (RBAC)
- Distributed Caching
- API Analytics
- Request Metrics

---

# Conclusion

The architecture is intentionally modular, allowing each component to evolve independently. This makes the project easier to maintain, test, and extend while demonstrating common backend engineering practices such as middleware-based request processing, JWT authentication, Redis-backed rate limiting, and centralized configuration.