# 🚀 Distributed Rate Limiter API Gateway

A production-style API Gateway built using **FastAPI**, **Redis**, and **JWT Authentication**. This project demonstrates middleware-based request processing, distributed sliding window rate limiting, authentication, and clean backend architecture.

---

## 📌 Features

- ✅ FastAPI REST API
- ✅ JWT Authentication
- ✅ Protected Routes
- ✅ Redis Integration
- ✅ Sliding Window Rate Limiter
- ✅ Logging Middleware
- ✅ Environment-based Configuration (.env)
- ✅ Modular Project Structure
- ✅ Health Check Endpoint
- ✅ Production-ready Folder Structure

---

## 🏗️ Tech Stack

- Python 3.12
- FastAPI
- Redis
- Uvicorn
- python-jose (JWT)
- python-dotenv
- Docker (Coming Soon)

---

## 📂 Project Structure

```
distributed-rate-limiter/
│
├── gateway/
│   ├── auth/
│   ├── core/
│   ├── middleware/
│   ├── routers/
│   ├── services/
│   ├── exceptions/
│   └── main.py
│
├── .env
├── .gitignore
├── requirements.txt
└── README.md
```

---

## ⚙️ Installation

### Clone Repository

```bash
git clone <your-repository-url>
```

### Create Virtual Environment

```bash
python -m venv venv
```

### Activate Virtual Environment

Windows

```bash
venv\Scripts\activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Start Redis

Make sure Redis is running on port **6379**.

### Run Application

```bash
uvicorn gateway.main:app --reload
```

---

## 📡 API Endpoints

### Authentication

| Method | Endpoint | Description |
|---------|----------|-------------|
| POST | `/auth/login` | Generate JWT Token |

### Users

| Method | Endpoint | Description |
|---------|----------|-------------|
| GET | `/users` | Protected Route |

### Products

| Method | Endpoint | Description |
|---------|----------|-------------|
| GET | `/products` | Product List |

### Health

| Method | Endpoint | Description |
|---------|----------|-------------|
| GET | `/health` | Health Check |

---

## 🔒 Authentication

All protected endpoints require a JWT token.

Example:

```
Authorization: Bearer <your_token>
```

---

## ⚡ Rate Limiting

This project implements a **Sliding Window Rate Limiter** backed by **Redis**.

Current Configuration:

- Requests: **5**
- Window: **60 seconds**

Configuration can be changed using the `.env` file.

---

## 🛠️ Future Improvements

- Docker Support
- Docker Compose
- Reverse Proxy
- Prometheus Monitoring
- Grafana Dashboard
- API Analytics
- Request Metrics

---


---

## 👨‍💻 Author

**Shubham Thakur**

Backend Developer | FastAPI | Python | Redis
