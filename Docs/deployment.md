# 🚀 Deployment Guide

## Overview

This document explains how to set up and run the **Distributed Rate Limiter API Gateway** on a local machine.

The project is built using **FastAPI**, **Redis**, and **JWT Authentication**. Before running the application, ensure that all required dependencies and services are installed.

---

# Prerequisites

Before running the project, install the following software.

| Software | Version |
|----------|---------|
| Python | 3.11+ |
| Redis | Latest Stable Version |
| Git | Latest Version |
| VS Code (Recommended) | Latest Version |

---

# Project Setup

## Step 1 — Clone the Repository

```bash
git clone <repository-url>
```

Move into the project directory.

```bash
cd distributed-rate-limiter
```

---

## Step 2 — Create Virtual Environment

Create a virtual environment.

```bash
python -m venv venv
```

---

## Step 3 — Activate Virtual Environment

### Windows

```powershell
venv\Scripts\activate
```

### Linux / macOS

```bash
source venv/bin/activate
```

---

## Step 4 — Install Dependencies

```bash
pip install -r requirements.txt
```

Verify installation.

```bash
pip list
```

---

# Environment Configuration

The application uses environment variables for configuration.

Create a `.env` file in the project root.

Example:

```env
APP_NAME=Distributed Rate Limiter Gateway
APP_VERSION=1.0.0

REDIS_HOST=localhost
REDIS_PORT=6379

JWT_SECRET_KEY=my_super_secret_key
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

RATE_LIMIT_REQUESTS=5
RATE_LIMIT_WINDOW=60

DEBUG=True
```

Never commit your real `.env` file to GitHub. Instead, provide a `.env.example` file with placeholder values.

---

# Starting Redis

Redis must be running before starting the FastAPI application.

If using Docker:

```bash
docker start redis-server
```

Verify Redis is running.

```bash
docker ps
```

Redis should appear in the list of running containers.

---

# Running the Application

Start the FastAPI server.

```bash
uvicorn gateway.main:app --reload
```

The application will start at:

```text
http://127.0.0.1:8000
```

Swagger documentation is available at:

```text
http://127.0.0.1:8000/docs
```

---

# Verifying the Application

Check the root endpoint.

```http
GET /
```

Expected response:

```json
{
    "success": true,
    "service": "Distributed Rate Limiter Gateway",
    "version": "1.0.0",
    "message": "Distributed Rate Limiter Gateway is running"
}
```

Health endpoint:

```http
GET /health
```

Expected response:

```json
{
    "success": true,
    "status": "healthy"
}
```

---

# Testing Authentication

Generate a JWT token.

```http
POST /auth/login
```

Copy the returned access token.

Authorize in Swagger by clicking **Authorize** and entering:

```text
Bearer <JWT Token>
```

Now test protected endpoints such as:

```http
GET /users
```

---

# Testing Rate Limiting

Send more than the configured number of requests within the configured time window.

Expected response:

```http
HTTP 429
```

```json
{
    "error": "Rate limit exceeded"
}
```

---

# Common Issues

## Redis Connection Error

Possible causes:

- Redis is not running.
- Incorrect host or port in `.env`.
- Docker container is stopped.

---

## JWT Authentication Error

Possible causes:

- Expired token.
- Invalid token.
- Incorrect JWT secret.

Expected response:

```http
HTTP 401 Unauthorized
```

---

## ModuleNotFoundError

Activate the virtual environment before running the project.

```powershell
venv\Scripts\activate
```

---

## Port Already in Use

Find the process using the port or change the port number.

Example:

```bash
uvicorn gateway.main:app --reload --port 8001
```

---

# Docker Support

Docker support will be added in a future update.

Planned additions:

- Dockerfile
- Docker Compose
- Multi-container deployment
- Automatic Redis startup

---

# Deployment Checklist

Before pushing the project to GitHub, ensure the following:

- Project runs without errors.
- Redis is configured correctly.
- `.env` is excluded using `.gitignore`.
- `requirements.txt` is updated.
- Documentation is complete.
- Screenshots are added.
- README is up to date.

---

# Conclusion

Following this guide should allow anyone to clone the repository, install the required dependencies, configure the environment, and run the project successfully. The project is designed to be easy to set up while demonstrating production-oriented backend development practices.