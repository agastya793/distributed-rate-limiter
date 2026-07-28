# 📡 Complete API Endpoint Reference Table

## Overview

The API Gateway exposes three categories of endpoints:
1. **Public Endpoints**: Open system endpoints for health checks, documentation, and login.
2. **Protected Proxy Endpoints**: Microservice routes requiring **Bearer JWT** or **X-API-Key** authentication and subject to sliding window rate limiting.
3. **Admin Management Endpoints**: Restricted management endpoints requiring the **X-Admin-Key** header.

---

## 🌐 1. Public & Documentation Endpoints

| Method | Endpoint | Auth Required | Rate Limited | Description |
| :--- | :--- | :---: | :---: | :--- |
| `GET` | `/` | ❌ | ❌ | Gateway root status & version information |
| `GET` | `/health` | ❌ | ❌ | Service health check |
| `GET` | `/dashboard` | ❌ | ❌ | Interactive Glassmorphism Web Dashboard & Rate Limit Simulator |
| `GET` | `/docs` | ❌ | ❌ | Interactive OpenAPI / Swagger UI |
| `GET` | `/openapi.json` | ❌ | ❌ | OpenAPI 3.1.0 schema specification |
| `GET` | `/redoc` | ❌ | ❌ | ReDoc interactive API documentation |
| `POST` | `/auth/login` | ❌ | ❌ | Authenticate user and issue signed Bearer JWT token |

---

## 🔒 2. Protected Reverse Proxy Endpoints

> **Authentication Header Required**: `Authorization: Bearer <JWT>` **OR** `X-API-Key: <API_KEY>`

| Method | Endpoint | Auth Required | Rate Limited | Target Microservice | Description |
| :--- | :--- | :---: | :---: | :--- | :--- |
| `GET` | `/users` | ✅ | ✅ | User Service (`8001`) | Proxies request to downstream User Service to fetch all users |
| `GET` | `/users/{id}` | ✅ | ✅ | User Service (`8001`) | Proxies request to User Service to fetch user by ID |
| `ANY` | `/users/{path}` | ✅ | ✅ | User Service (`8001`) | Reverse proxies any HTTP method & sub-path to User Service |
| `GET` | `/users/limit` | ✅ | ✅ | Gateway Local | Returns active rate limit for current API Key client |
| `GET` | `/products` | ✅ | ✅ | Product Service (`8002`)| Proxies request to downstream Product Service to fetch products |
| `GET` | `/products/{id}`| ✅ | ✅ | Product Service (`8002`)| Proxies request to Product Service to fetch product by ID |
| `ANY` | `/products/{path}`| ✅ | ✅ | Product Service (`8002`)| Reverse proxies any HTTP method & sub-path to Product Service |

---

## 🔑 3. Admin & Observability Endpoints

> **Authentication Header Required**: `X-Admin-Key: <ADMIN_KEY>` (e.g. `admin-secret-key-12345`)

| Method | Endpoint | Required Header | Description |
| :--- | :--- | :---: | :--- |
| `POST` | `/admin/api-key/{client}` | `X-Admin-Key` | Generate cryptographically secure 32-byte hex API Key for client |
| `DELETE`| `/admin/api-key/{api_key}` | `X-Admin-Key` | Revoke existing API Key immediately |
| `POST` | `/admin/rate-limit` | `X-Admin-Key` | Set dynamic custom rate limit override for a specific client |
| `GET` | `/admin/rate-limit/{client}`| `X-Admin-Key` | Retrieve active rate limit for a client |
| `GET` | `/admin/rate-limits` | `X-Admin-Key` | Retrieve all custom rate limit overrides stored in Redis |
| `DELETE`| `/admin/rate-limit/{client}`| `X-Admin-Key` | Remove custom limit override (reverts to client role default) |
| `POST` | `/admin/role` | `X-Admin-Key` | Assign client role (`free`: 10/m, `premium`: 100/m, `admin`: 1M/m) |
| `POST` | `/admin/whitelist/{client}` | `X-Admin-Key` | Add client to whitelist (bypasses rate limiter) |
| `POST` | `/admin/blacklist/{client}` | `X-Admin-Key` | Add client to blacklist (returns `403 Forbidden`) |
| `DELETE`| `/admin/blacklist/{client}` | `X-Admin-Key` | Remove client from blacklist |
| `GET` | `/admin/metrics` | `X-Admin-Key` | Retrieve real-time request counts, latency, and Redis diagnostics |
| `DELETE`| `/admin/metrics` | `X-Admin-Key` | Reset all accumulated metric counters in Redis |
