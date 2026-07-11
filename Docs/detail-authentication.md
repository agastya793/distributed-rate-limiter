# 🔐 Authentication

## Overview

This project secures protected API endpoints using **JSON Web Tokens (JWT)**.

Instead of maintaining user sessions on the server, authentication is handled using stateless JWT tokens. After a successful login, the client receives a signed token, which must be included in every request to protected endpoints.

---

# Authentication Flow

```text
                  User Login
                       │
                       ▼
        Username + Password Received
                       │
                       ▼
            JWT Token Generated
                       │
                       ▼
           Token Sent to Client
                       │
                       ▼
      Client Stores JWT Securely
                       │
                       ▼
 Authorization: Bearer <JWT Token>
                       │
                       ▼
          FastAPI API Gateway
                       │
                       ▼
           JWT Verification
                       │
             ┌─────────┴─────────┐
             │                   │
             ▼                   ▼
      Token Valid          Token Invalid
             │                   │
             ▼                   ▼
    Execute Route        Return HTTP 401
```

---

# Login Process

When a client sends valid credentials to the login endpoint, the gateway generates a JWT containing the user's information.

Example request:

```http
POST /auth/login

{
    "username": "shubham",
    "password": "********"
}
```

Example response:

```json
{
    "access_token": "<JWT Token>"
}
```

---

# JWT Structure

A JWT consists of three parts.

```text
Header.Payload.Signature
```

Example

```text
xxxxx.yyyyy.zzzzz
```

---

## 1. Header

Contains information about the signing algorithm.

Example

```json
{
    "alg": "HS256",
    "typ": "JWT"
}
```

---

## 2. Payload

Contains user-related information.

Example

```json
{
    "username": "shubham",
    "exp": 1783719690
}
```

The expiration time (`exp`) ensures the token becomes invalid after a configured duration.

---

## 3. Signature

The signature prevents token tampering.

It is generated using:

- Header
- Payload
- Secret Key

If any part of the token changes, signature verification fails.

---

# Protected Routes

Every protected endpoint requires the following HTTP header.

```http
Authorization: Bearer <JWT Token>
```

Example

```http
GET /users

Authorization: Bearer eyJhbGc...
```

The gateway extracts the token, verifies its signature, validates the expiration time, and grants access only if the token is valid.

---

# Authentication Components

## jwt_handler.py

Responsible for

- Creating JWT tokens
- Verifying JWT tokens
- Validating expiration time

---

## dependencies.py

Acts as an authentication dependency for protected routes.

Responsibilities:

- Extract token from Authorization header
- Verify JWT
- Return authenticated user information
- Reject invalid requests

---

## auth.py

Provides the authentication endpoints.

Current endpoint:

```
POST /auth/login
```

---

# Authentication Workflow

```text
Client
    │
    ▼
Login Request
    │
    ▼
JWT Generated
    │
    ▼
Client Receives Token
    │
    ▼
Stores Token
    │
    ▼
Protected Request
    │
    ▼
Verify JWT
    │
    ▼
Execute Protected Route
```

---

# Error Responses

Invalid or expired tokens return:

```json
{
    "detail": "Invalid or expired token"
}
```

HTTP Status:

```
401 Unauthorized
```

---

# Security Notes

This project uses JWT-based authentication for learning purposes.

In a production environment, additional security measures should be considered, including:

- Password hashing
- Refresh tokens
- Secure secret management
- HTTPS
- Token revocation
- Role-Based Access Control (RBAC)

---

# Key Learning Outcomes

Through this implementation, the following backend concepts were explored:

- JWT-based authentication
- Stateless authorization
- Protected API routes
- Dependency Injection in FastAPI
- Token verification
- Secure API design