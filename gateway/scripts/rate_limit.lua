local key = KEYS[1]

local now = tonumber(ARGV[1])

local window = tonumber(ARGV[2])

local limit = tonumber(ARGV[3])

redis.call(
    "ZREMRANGEBYSCORE",
    key,
    0,
    now - window
)

local count = redis.call(
    "ZCARD",
    key
)

if count >= limit then
    return 0
end

redis.call(
    "ZADD",
    key,
    now,
    tostring(now)
)

redis.call(
    "EXPIRE",
    key,
    window
)

return 1