
# 🚦 Sliding Window Rate Limiter

## Table of Contents

- Introduction
- What is Rate Limiting?
- Why APIs Need Rate Limiting
- Real-World Example
- What is a Sliding Window Rate Limiter?
- How the Sliding Window Algorithm Works
- Step-by-Step Request Flow
- Sliding Window Visualization
- Redis Implementation
- Redis Sorted Set (ZSET)
- Redis Commands Used
- Advantages
- Limitations
- Time Complexity
- Project Implementation
- Future Improvements


---

# Introduction

A **Sliding Window Rate Limiter** is an algorithm used to control how many requests a client can send to an API within a specific time period.

In this project, it is implemented using **FastAPI** and **Redis** to protect API endpoints from excessive traffic and abuse.

Instead of simply counting requests, the Sliding Window algorithm continuously evaluates requests over the **most recent time window**, making it more accurate than many other rate limiting techniques.

---

# What is Rate Limiting?

Rate limiting is a technique that controls how frequently a client can access an API.

For example,

- Maximum Requests: **5**
- Time Window: **60 Seconds**

This means a client can send **only five requests within any sixty-second period**.

If the client exceeds the limit, the API returns:

```http
HTTP 429 Too Many Requests
```

instead of processing the request.

---

# Why APIs Need Rate Limiting

Without rate limiting, an API can receive unlimited requests from a single client.

This can lead to:

- Server overload
- High infrastructure costs
- Denial of Service (DoS)
- Brute-force login attacks
- API abuse
- Poor experience for legitimate users

Rate limiting ensures that every client gets fair access to the API.

---

# Real-World Example

Imagine a movie ticket booking website.

A user repeatedly refreshes the booking page hundreds of times every second.

Without rate limiting:

```
User

↓

1000 Requests / Second

↓

Server Crash
```

With Sliding Window Rate Limiting:

```
User

↓

5 Requests Allowed

↓

6th Request

↓

HTTP 429
```

The server remains stable while preventing abuse.

---

# What is a Sliding Window Rate Limiter?

The Sliding Window algorithm checks how many requests have been made during the **last N seconds**, rather than using fixed intervals.

Unlike a Fixed Window algorithm, the time window continuously moves forward.

This makes request counting much fairer.

---

# How the Sliding Window Algorithm Works

Suppose:

```
Request Limit = 5

Time Window = 60 Seconds
```

Every new request follows these steps.

### Step 1

Receive the incoming request.

↓

### Step 2

Remove request timestamps older than 60 seconds.

↓

### Step 3

Count how many timestamps remain.

↓

### Step 4

If the count is less than 5,

Allow the request.

Otherwise,

Return

```
HTTP 429
Too Many Requests
```

---

# Step-by-Step Request Flow

```
Client Request
        │
        ▼
Receive Current Time
        │
        ▼
Remove Expired Requests
        │
        ▼
Count Active Requests
        │
        ├───────────────┐
        │               │
        ▼               ▼
Count < Limit      Count ≥ Limit
        │               │
        ▼               ▼
Store Timestamp   Return HTTP 429
        │
        ▼
Execute Route
        │
        ▼
Return Response
```

---

# Sliding Window Visualization

Current Configuration

```
Maximum Requests = 5

Window = 60 Seconds
```

### Example 1

```
Time →

|--------------------60 Seconds--------------------|

1️⃣   2️⃣   3️⃣   4️⃣   5️⃣

✅ All requests allowed
```

---

### Example 2

```
Time →

|--------------------60 Seconds--------------------|

1️⃣   2️⃣   3️⃣   4️⃣   5️⃣   6️⃣

                     ❌ Rejected

HTTP 429
```

The sixth request is rejected because five requests already exist inside the active window.

---

### Example 3

```
Time →

|--------------------60 Seconds--------------------|

1️⃣   2️⃣   3️⃣   4️⃣   5️⃣

            60 Seconds Pass

↓

2️⃣   3️⃣   4️⃣   5️⃣

↓

1️⃣ automatically expires

↓

6️⃣ arrives

↓

✅ Allowed
```

This is why the algorithm is called **Sliding Window**.

The window continuously moves with time.

---

# Redis Implementation

Instead of storing request timestamps in Python memory, this project stores them inside Redis.

Redis provides:

- Fast in-memory storage
- Automatic expiration
- High performance
- Shared storage between multiple servers

This makes it suitable for production systems.

---

# Redis Sorted Set (ZSET)

The Sliding Window algorithm uses a Redis **Sorted Set**.

Each request timestamp is stored as both:

- Member
- Score

Example

```
Key

sliding:127.0.0.1
```

Stored Data

```
------------------------------------
Timestamp        Score
------------------------------------
1720800001       1720800001
1720800010       1720800010
1720800025       1720800025
1720800038       1720800038
1720800054       1720800054
------------------------------------
```

Because Redis keeps the timestamps sorted automatically, removing old requests becomes very efficient.

---

# Redis Commands Used

### ZADD

Adds the current request timestamp.

```
Redis

↓

ZADD
```

---

### ZCARD

Counts how many requests currently exist.

```
Redis

↓

ZCARD

↓

Current Request Count
```

---

### ZREMRANGEBYSCORE

Removes timestamps older than the configured time window.

```
Old Requests

↓

Deleted
```

---

### EXPIRE

Automatically deletes inactive keys after the configured window.

This prevents unnecessary memory usage.

---

# Advantages

The Sliding Window algorithm provides several benefits.

- Accurate request counting
- Fair request limiting
- Prevents sudden traffic bursts
- Efficient Redis implementation
- Suitable for production APIs
- Better than Fixed Window for most applications

---

# Limitations

Although effective, the Sliding Window algorithm has some limitations.

- Uses more memory than Fixed Window
- Requires Redis
- Slightly more complex implementation
- Additional Redis operations per request

---

# Time Complexity

| Operation | Complexity |
|------------|------------|
| Add Request | O(log N) |
| Remove Expired Requests | O(log N + M) |
| Count Requests | O(1) |

Where:

- **N** = Total stored timestamps
- **M** = Expired timestamps removed

---

# Project Implementation

The implementation is located in:

```
gateway/middleware/sliding_window.py
```

The middleware performs the following operations for every incoming request.

1. Receive request
2. Read client IP
3. Calculate current timestamp
4. Remove expired timestamps
5. Count active requests
6. Compare with configured limit
7. Reject or allow request
8. Store current timestamp
9. Continue processing

Because the middleware executes before route handlers, every endpoint is automatically protected.

---

# Future Improvements

Possible improvements include:

- User-based rate limiting
- API key rate limiting
- Role-based rate limits
- Distributed deployments
- Dynamic configuration
- Monitoring using Prometheus
- Grafana dashboards
- Request analytics

