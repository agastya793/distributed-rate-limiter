# 🔄 Request Flow

## Overview

Every request sent to the API Gateway follows a predefined processing pipeline before reaching the requested endpoint.

Instead of directly executing business logic, the request passes through several layers responsible for logging, security, and rate limiting.

This layered architecture improves maintainability, security, and scalability.

---

# Complete Request Lifecycle

```text
                    Client
                      │
                      │ HTTP Request
                      ▼
          FastAPI API Gateway
                      │
                      ▼
            Logging Middleware
                      │
                      ▼
      Sliding Window Rate Limiter
                      │
                      ▼
         Authentication (JWT)
                      │
            ┌─────────┴─────────┐
            │                   │
            ▼                   ▼
      Token Valid         Token Invalid
            │                   │
            ▼                   ▼
      Route Handler       HTTP 401
            │
            ▼
      Business Logic
            │
            ▼
      JSON Response
            │
            ▼
           Client
```

---

# Step 1 – Client Sends Request

The process starts when a client sends an HTTP request.

Example

```http
GET /users

Authorization: Bearer <JWT Token>
```

At this stage, the gateway has not yet validated the request.

---

# Step 2 – Request Reaches FastAPI Gateway

The FastAPI application receives every incoming request.

Responsibilities:

- Identify requested endpoint
- Execute middleware
- Route request to the correct handler

File

```
gateway/main.py
```

---

# Step 3 – Logging Middleware

Before any business logic executes, the request passes through the logging middleware.

Responsibilities

- Record HTTP Method
- Record Request Path
- Measure Processing Time
- Print Request Log

Example Log

```text
GET /users

Status : 200

Execution Time : 3.12 ms
```

Benefits

- Easier debugging
- Performance monitoring
- Request tracking

---

# Step 4 – Sliding Window Rate Limiter

Every request is checked against the configured rate limit.

Current Configuration

```text
Maximum Requests : 5

Window : 60 Seconds
```

Processing Steps

```text
Receive Request

↓

Remove Expired Requests

↓

Count Active Requests

↓

Within Limit ?
```

If the limit has been exceeded

↓

Return

```text
HTTP 429

Too Many Requests
```

Otherwise

↓

Continue processing.

---

# Step 5 – Authentication

Protected endpoints require a valid JWT.

Authentication Process

```text
Read Authorization Header

↓

Extract JWT

↓

Verify Signature

↓

Check Expiration

↓

Decode Payload

↓

Return User Information
```

If verification fails

↓

Return

```text
HTTP 401

Unauthorized
```

---

# Step 6 – Route Execution

Once middleware and authentication succeed, the request reaches the appropriate route handler.

Example

```text
GET /users
```

Responsibilities

- Execute business logic
- Prepare response
- Return JSON

---

# Step 7 – Response Returned

The application generates a JSON response.

Example

```json
{
    "success": true,
    "message": "Users fetched successfully",
    "data": {
        "users": [
            "Alice",
            "Bob",
            "Charlie"
        ]
    }
}
```

The response is then returned to the client.

---

# Error Flow

The request may terminate early if validation fails.

```text
Request

↓

Logging

↓

Rate Limiter

↓

Too Many Requests

↓

HTTP 429
```

or

```text
Request

↓

Logging

↓

JWT Verification

↓

Invalid Token

↓

HTTP 401
```

Only valid requests continue to the business logic.

---

# Why Middleware Is Used

Instead of placing logging and rate limiting inside every endpoint, middleware processes every request automatically.

Advantages

- No duplicate code
- Cleaner route handlers
- Easier maintenance
- Consistent request handling

---

# Summary

Every request passes through multiple validation and processing stages before business logic is executed.

This architecture ensures:

- Consistent request processing
- Authentication for protected endpoints
- Centralized logging
- Redis-backed rate limiting
- Clean separation of responsibilities

The result is a modular and production-oriented request pipeline that can be extended with additional middleware such as caching, monitoring, or authorization in the future.