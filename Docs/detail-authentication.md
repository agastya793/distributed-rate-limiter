# 🔐 Dual Security & Authentication Architecture

## Overview

The API Gateway implements a production-style **Dual Security Architecture** supporting both **Stateless JSON Web Tokens (JWT)** and **Redis-Backed Client API Keys (`X-API-Key`)**, along with an isolated **Admin Key (`X-Admin-Key`)** for management operations.

This dual-tier approach allows human users (web/mobile apps) to authenticate via standard JWT OAuth2 Bearer workflows, while automated server-to-server API clients authenticate using high-performance API Keys.

---

# Dual Authentication Flow

```text
                               Client Request
                                     │
                                     ▼
                        FastAPI API Gateway (Port 8000)
                                     │
       ┌─────────────────────────────┼─────────────────────────────┐
       │                             │                             │
       ▼                             ▼                             ▼
Authorization: Bearer <JWT>     Header: X-API-Key           Header: X-Admin-Key
 (JWT Bearer Token)              (Client API Key)            (Admin Management)
       │                             │                             │
       ▼                             ▼                             ▼
 Decode & Verify             Validate via Redis           Compare with Config
 `jwt_handler.verify_token`  `api_key_service`            `settings.ADMIN_KEY`
       │                             │                             │
       ├─────────────────────────────┴─────────────────────────────┤
       │                                                           │
       ▼                                                           ▼
 Valid Identity                                            Invalid / Missing
       │                                                           │
       ▼                                                           ▼
Execute Route / Proxy                                     HTTP 401 / 403 Error
```

---

# 🔑 Authentication Methods

## 1. JWT Bearer Token Authentication

Used for user logins via `POST /auth/login`.

### Login Request

```http
POST /auth/login HTTP/1.1
Host: localhost:8000
Content-Type: application/json

{
  "username": "shubham",
  "password": "password123"
}
```

### Login Response

```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### JWT Structure & Claims

A JWT consists of three base64url-encoded parts separated by dots (`Header.Payload.Signature`):

1. **Header**: Algorithmic metadata (`{"alg": "HS256", "typ": "JWT"}`).
2. **Payload**: Authenticated user claims:
   ```json
   {
     "sub": "shubham",
     "username": "shubham",
     "role": "admin",
     "exp": 1783719690
   }
   ```
3. **Signature**: Cryptographic hash generated using `HS256` secret key (`settings.JWT_SECRET_KEY`).

### Protected Request with JWT

```http
GET /users HTTP/1.1
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

---

## 2. Client API Key Authentication (`X-API-Key`)

Used for automated background scripts and third-party API clients.

### API Key Generation (Admin Endpoint)

```http
POST /admin/api-key/my_client HTTP/1.1
X-Admin-Key: admin-secret-key-12345
```

### Response

```json
{
  "client": "my_client",
  "api_key": "4a2b8c9d1e3f5a7b9c1d3e5f7a9b1c3d5e7f9a1b3c5d7e9f1a3b5c7d9e1f3a5b"
}
```

### Protected Request with API Key

```http
GET /products HTTP/1.1
X-API-Key: 4a2b8c9d1e3f5a7b9c1d3e5f7a9b1c3d5e7f9a1b3c5d7e9f1a3b5c7d9e1f3a5b
```

---

## 3. Admin Key Authorization (`X-Admin-Key`)

Restricts access to administrative endpoints (`/admin/*`) managing rate limits, API keys, client roles, whitelists, blacklists, and metrics.

```http
GET /admin/metrics HTTP/1.1
X-Admin-Key: admin-secret-key-12345
```

---

# 🛠️ Code Components & Architecture

### 1. `gateway/auth/jwt_handler.py`
Provides stateless JWT utility functions:
- `create_access_token(data: dict)`: Generates signed JWTs with expiration timestamps using `python-jose`.
- `verify_token(token: str)`: Decodes and verifies token signatures and expiration; returns payload dict or `None`.

### 2. `gateway/services/api_key_service.py`
Manages Redis-backed API Key storage:
- `generate_api_key(client: str)`: Generates a cryptographically secure 32-byte hex token (`secrets.token_hex(32)`) and stores `api_key:<token> ──▶ client` in Redis.
- `validate_api_key(api_key: str)`: `$O(1)$` Redis lookup to resolve client identity.
- `revoke_api_key(api_key: str)`: Deletes key mapping instantly.

### 3. `gateway/auth/dependencies.py`
Provides FastAPI Dependency Injection security functions:
- `get_current_user`: Extracts and verifies JWT Bearer tokens from `Authorization` header.
- `get_current_client`: Accepts **EITHER** a valid JWT Bearer token OR a valid `X-API-Key` header, returning the resolved `client` identifier.

### 4. `gateway/middleware/sliding_window.py`
Enforces early dual-authentication and rate limiting before requests hit routers:
- Checks public path bypasses (`/`, `/health`, `/docs`, `/auth/login`, `/admin/*`).
- Extracts and validates `X-API-Key` or `Authorization: Bearer <token>`.
- Evaluates blacklists (`HTTP 403`), whitelists, and executes `rate_limit.lua` on Redis Sorted Sets.

---

# ❌ Error Handling & Status Codes

| Scenario | HTTP Status | Response Payload |
| :--- | :--- | :--- |
| **Missing Credentials** | `401 Unauthorized` | `{"error": "Valid JWT Bearer token or X-API-Key is required"}` |
| **Expired / Invalid JWT** | `401 Unauthorized` | `{"detail": "Invalid or expired token"}` |
| **Invalid API Key** | `401 Unauthorized` | `{"detail": "Invalid API Key"}` |
| **Blacklisted Client** | `403 Forbidden` | `{"error": "Client is blacklisted"}` |
| **Invalid Admin Key** | `403 Forbidden` | `{"detail": "Invalid or missing X-Admin-Key header"}` |

---

# 🔒 Security Best Practices Implemented

- **Dual-Auth Flexibility**: Seamless support for both interactive users (JWT) and automated services (API Keys).
- **Stateless Verification**: JWT validation occurs in-memory without database bottlenecks.
- **Cryptographic Security**: Uses `secrets.token_hex(32)` for unguessable API Keys and `HS256` signed JWTs.
- **Strict Role Isolation**: Admin operations require dedicated `X-Admin-Key` verification.
- **Fast Revocation**: API Keys stored in Redis can be revoked instantly via `/admin/api-key/{key}` without restarting services.