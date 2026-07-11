## 🏗️ System Architecture

```text
                     Client
                        │
                        ▼
                FastAPI API Gateway
        ┌───────────────┼────────────────┐
        │               │                │
        ▼               ▼                ▼
 Authentication   Logging Middleware   Sliding Window
      │                                  Rate Limiter
      │                                       │
      ▼                                       ▼
 JWT Token Validation                    Redis Cache
      │                                       │
      └───────────────┬───────────────────────┘
                      ▼
                 Route Handler
                      │
                      ▼
                 JSON Response
```



below it , explain each component:



| Component                   | Purpose                                         |
| --------------------------- | ----------------------------------------------- |
| API Gateway                 | Receives every request                          |
| JWT Authentication          | Verifies user identity                          |
| Logging Middleware          | Logs request method, endpoint and response time |
| Sliding Window Rate Limiter | Prevents API abuse                              |
| Redis                       | Stores request timestamps                       |
| Route Handler               | Executes business logic                         |
