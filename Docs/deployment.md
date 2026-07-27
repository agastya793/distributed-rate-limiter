# 🚀 Comprehensive Local & Docker Deployment Guide

## Overview

This guide provides step-by-step instructions for running the **Distributed Rate Limiter API Gateway & Microservices System** locally using Python or via single-command multi-container orchestration with **Docker Compose**.

The system consists of **4 active services**:
1. **FastAPI API Gateway** (`Port 8000`)
2. **Redis In-Memory Database** (`Port 6379`)
3. **User Microservice** (`Port 8001`)
4. **Product Microservice** (`Port 8002`)

---

# Prerequisites

Ensure the following tools are installed on your machine:

| Software | Minimum Version | Recommended Version |
| :--- | :--- | :--- |
| **Python** | 3.10+ | 3.11+ |
| **Redis** | 6.2+ | 7.2+ |
| **Docker & Docker Compose** | 20.10+ | Latest Desktop |
| **Git** | 2.30+ | Latest |

---

# Option A: Running via Docker Compose (Recommended - 1 Command)

Running with Docker Compose boots all 4 containers (`redis`, `gateway`, `user-service`, `product-service`) inside an isolated bridge network (`gateway-network`) with automatic health checks.

### 1. Build and Launch Containers

```bash
docker compose up --build
```

### 2. Verify Running Services

```bash
docker compose ps
```

Expected active containers:
- `api-gateway` (`http://localhost:8000`)
- `user-service` (`http://localhost:8001`)
- `product-service` (`http://localhost:8002`)
- `redis-server` (`localhost:6379`)

To stop all containers:
```bash
docker compose down
```

---

# Option B: Local Python Development Setup

If developing locally without Docker, follow these steps:

## Step 1 — Clone Repository & Setup Virtual Environment

```bash
git clone <repository-url>
cd distributed-rate-limiter

python -m venv venv
```

Activate environment:
- **Windows (PowerShell)**: `venv\Scripts\activate`
- **Linux / macOS**: `source venv/bin/activate`

---

## Step 2 — Install Python Dependencies

```bash
pip install -r requirements.txt
```

---

## Step 3 — Configure Environment Variables (`.env`)

Create a `.env` file in the root directory:

```env
APP_NAME=Distributed Rate Limiter Gateway
APP_VERSION=1.0.0

REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=

JWT_SECRET_KEY=my_super_secret_key
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

ADMIN_KEY=admin-secret-key-12345

RATE_LIMIT_REQUESTS=10
RATE_LIMIT_WINDOW=60

USER_SERVICE_URL=http://127.0.0.1:8001
PRODUCT_SERVICE_URL=http://127.0.0.1:8002

DEBUG=True
```

---

## Step 4 — Start Local Services

Ensure Redis is running on port `6379` (`redis-server`).

Open 3 terminal windows to launch the services:

### Terminal 1: User Microservice (Port 8001)
```powershell
venv\Scripts\activate
python -m uvicorn services.user_service.main:app --port 8001
```

### Terminal 2: Product Microservice (Port 8002)
```powershell
venv\Scripts\activate
python -m uvicorn services.product_service.main:app --port 8002
```

### Terminal 3: API Gateway (Port 8000)
```powershell
venv\Scripts\activate
python -m uvicorn gateway.main:app --port 8000 --reload
```

---

# 🧪 Verification & System Health Checks

### 1. Root Gateway Status
```http
GET http://localhost:8000/
```
**Response**:
```json
{
  "success": true,
  "service": "Distributed Rate Limiter Gateway",
  "version": "1.0.0",
  "message": "Distributed Rate Limiter Gateway is running"
}
```

### 2. Gateway Health Endpoint
```http
GET http://localhost:8000/health
```
**Response**: `{"success": true, "status": "healthy"}`

### 3. Interactive Documentation
Open browser at: `http://localhost:8000/docs`

---

# 🧪 Running Automated Tests

Execute the complete integration and unit test suite using `pytest`:

```powershell
python -m pytest gateway/tests/ -v
```

Expected output:
```text
gateway/tests/test_admin.py PASSED                                     [ 25%]
gateway/tests/test_auth.py PASSED                                      [ 50%]
gateway/tests/test_health.py PASSED                                     [ 75%]
gateway/tests/test_proxy.py PASSED                                      [100%]

============================== 4 passed in 0.35s ==============================
```

---

# 🛠️ Common Troubleshooting & Issues

### 1. Port Already in Use (Errno 10048)
If port `8001`, `8002`, or `8000` is already in use by another process:
- On Windows PowerShell: `Get-Process -Id (Get-NetTCPConnection -LocalPort 8001).OwningProcess | Stop-Process -Force`
- Or specify a different port when launching `uvicorn`.

### 2. Redis Connection Refused
- Verify Redis is running: `redis-cli ping` (should respond `PONG`).
- If running Docker Redis, check container status: `docker ps`.

### 3. Rate Limiting 429 Errors
- By default, free role users receive a limit of **10 requests / 60 seconds**.
- To reset rate limits or view stats, query `GET http://localhost:8000/admin/metrics` using header `X-Admin-Key: admin-secret-key-12345`.