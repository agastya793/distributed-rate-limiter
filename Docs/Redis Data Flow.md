# 🧠 Redis Data Flow & Memory Schema

## Overview

In the API Gateway, **Redis (`redis.asyncio`)** serves as the high-speed, non-blocking in-memory data store.

It powers:
1. **Atomic Sliding Window Rate Limiting** using Sorted Sets (`ZSET`) and Lua scripts.
2. **Client Identity & API Keys** validation.
3. **Dynamic Policies** (custom limits, role-based limits, whitelisting, and blacklisting).
4. **Real-time Observability Metrics** (request counts, status codes, and latency histograms).

---

# Atomic Redis Rate Limit Data Flow

```text
                     Incoming HTTP Request
                               │
                               ▼
               FastAPI SlidingWindowRateLimiter
                               │
                               ▼
                Dynamic Limit & Role Lookup
       (From Redis `rate_limit:<client>` or Role default)
                               │
                               ▼
                redis_service.rate_limit_script
           (Executes `rate_limit.lua` Atomically on Redis)
                               │
                               ▼
 ┌───────────────────────────────────────────────────────────┐
 │               ATOMIC REDIS LUA SCRIPT ENGINE              │
 │                                                           │
 │ 1. ZREMRANGEBYSCORE sliding:<client> 0 (now - window)     │
 │    ──▶ Drop all expired timestamps outside 60s window     │
 │                                                           │
 │ 2. ZCARD sliding:<client>                                 │
 │    ──▶ Count remaining active timestamps in sorted set    │
 │                                                           │
 │ 3. Evaluation: Is (count >= limit)?                       │
 └─────────────────────────────┬─────────────────────────────┘
                               │
             ┌─────────────────┴─────────────────┐
             │                                   │
       YES (count >= limit)               NO (count < limit)
             │                                   │
             ▼                                   ▼
   Return 0 (Denied)                    4. seq = INCR sliding:<client>:seq
             │                          5. member = now .. ":" .. seq
             ▼                          6. ZADD sliding:<client> now member
  HTTP 429 Too Many Requests            7. EXPIRE sliding:<client> window
  - X-RateLimit-Limit: N                8. Return 1 (Allowed)
  - X-RateLimit-Remaining: 0                     │
  - Retry-After: 60                              ▼
                                       HTTP 200 OK / Proxied
                                       - X-RateLimit-Limit: N
```

---

# Redis Key Schema & Data Types

The gateway organizes data in Redis using strict key prefixes to ensure fast `$O(1)$` and `$O(\log N)$` lookups:

| Key Pattern | Redis Type | Description & Example Value |
| :--- | :--- | :--- |
| `sliding:<client>` | `ZSET` (Sorted Set) | Stores active request scores (timestamps) and unique members (`<timestamp>:<sequence>`). |
| `sliding:<client>:seq` | `STRING` (Counter) | Atomic integer incremented via `INCR` to guarantee unique member names for millisecond-level parallel requests. |
| `api_key:<api_key>` | `STRING` | Maps hex API key to `client_id` (e.g. `api_key:a1b2c3... ──▶ "shubham"`). |
| `rate_limit:<client>` | `STRING` | Dynamic custom rate limit override set via `/admin/rate-limit` (e.g. `"50"`). |
| `user_role:<client>` | `STRING` | Client role assignment (`"free"`, `"premium"`, `"admin"`). |
| `whitelist_clients` | `SET` | Set of whitelisted client IDs that bypass rate limiting. |
| `blacklist_clients` | `SET` | Set of blacklisted client IDs that receive immediate `HTTP 403 Forbidden`. |
| `metrics:total_requests` | `STRING` (Counter) | Total number of HTTP requests processed by Gateway. |
| `metrics:total_duration_ms` | `STRING` (Float) | Cumulative processing duration in milliseconds. |
| `metrics:success_requests` | `STRING` (Counter) | Count of `2xx` / `3xx` successful HTTP responses. |
| `metrics:rate_limited_requests` | `STRING` (Counter) | Count of `429` Rate Limited responses. |
| `metrics:failed_requests` | `STRING` (Counter) | Count of `4xx` / `5xx` error responses. |
| `metrics:endpoint:<method>:<path>`| `STRING` (Counter) | Per-endpoint request hit breakdown (e.g. `metrics:endpoint:GET:/users ──▶ 150`). |
| `metrics:client:<client_id>` | `STRING` (Counter) | Per-client total request breakdown. |

---

# Why Redis Sorted Sets (`ZSET`) + Lua Script?

### 1. Fixed Window vs. Sliding Window
- **Fixed Window**: Resets counters at fixed boundaries (e.g. every minute on the clock). A client can burst double their limit at boundary edges (e.g., 10 requests at 12:00:59 and 10 requests at 12:01:01).
- **Sliding Window**: Tracks exact timestamps over a rolling 60-second window, completely eliminating boundary burst vulnerabilities.

### 2. Single Round-Trip Atomicity
Without Lua scripting, calculating a sliding window requires 4 separate Redis network calls:
1. `ZREMRANGEBYSCORE`
2. `ZCARD`
3. `ZADD`
4. `EXPIRE`

Under high concurrency, running these commands separately creates **race conditions** where multiple requests read old counts simultaneously, allowing clients to breach rate limits.

By executing `rate_limit.lua`, Redis runs all operations **atomically in a single thread**, guaranteeing zero race conditions and reducing network round-trips from **4 to 1**.

---

# Real-time Metrics Retrieval (`/admin/metrics`)

When an admin queries `GET /admin/metrics` with `X-Admin-Key: admin-secret-key-12345`:

1. `MetricsService` reads `metrics:total_requests`, `metrics:total_duration_ms`, `metrics:success_requests`, and `metrics:rate_limited_requests`.
2. Computes average latency: `average_latency_ms = total_duration_ms / total_requests`.
3. Scans `metrics:endpoint:*` keys using `SCAN_ITER` to assemble endpoint hit breakdown.
4. Calls `client.info()` to fetch Redis engine diagnostics (`used_memory_human`, `connected_clients`, `uptime_in_seconds`, `redis_version`).
5. Returns consolidated JSON report to the admin client.