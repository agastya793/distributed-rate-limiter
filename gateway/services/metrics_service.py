from gateway.services.redis_service import redis_service


class MetricsService:

    def __init__(self):
        self.client = redis_service.get_client()

    async def record_request(
        self,
        method: str,
        path: str,
        status_code: int,
        duration_ms: float,
        client_id: str = "anonymous"
    ):
        try:
            await self.client.incr("metrics:total_requests")
            await self.client.incrbyfloat("metrics:total_duration_ms", duration_ms)

            # Status code counters
            if 200 <= status_code < 400:
                await self.client.incr("metrics:success_requests")
            elif status_code == 429:
                await self.client.incr("metrics:rate_limited_requests")
                await self.client.incr("metrics:failed_requests")
            else:
                await self.client.incr("metrics:failed_requests")

            # Per-endpoint stats
            endpoint_key = f"metrics:endpoint:{method.upper()}:{path}"
            await self.client.incr(endpoint_key)

            # Per-client stats
            if client_id and client_id != "anonymous":
                client_key = f"metrics:client:{client_id}"
                await self.client.incr(client_key)
        except Exception:
            # Prevent metrics recording failures from breaking request execution
            pass

    async def get_metrics(self):
        try:
            async def get_val(key):
                val = await self.client.get(key)
                return float(val) if val else 0.0

            total_reqs = int(await get_val("metrics:total_requests"))
            success_reqs = int(await get_val("metrics:success_requests"))
            failed_reqs = int(await get_val("metrics:failed_requests"))
            rate_limited_reqs = int(await get_val("metrics:rate_limited_requests"))
            total_duration = await get_val("metrics:total_duration_ms")

            avg_latency_ms = round(total_duration / total_reqs, 2) if total_reqs > 0 else 0.0

            # Gather endpoint breakdown
            endpoints = {}
            async for key in self.client.scan_iter(match="metrics:endpoint:*"):
                val = await self.client.get(key)
                clean_name = key.replace("metrics:endpoint:", "")
                endpoints[clean_name] = int(val) if val else 0

            # Redis info statistics
            redis_stats = {}
            try:
                info = await self.client.info()
                redis_stats = {
                    "redis_version": info.get("redis_version"),
                    "used_memory_human": info.get("used_memory_human"),
                    "connected_clients": info.get("connected_clients"),
                    "uptime_in_seconds": info.get("uptime_in_seconds"),
                }
            except Exception:
                redis_stats = {"status": "offline"}

            return {
                "summary": {
                    "total_requests": total_reqs,
                    "success_requests": success_reqs,
                    "failed_requests": failed_reqs,
                    "rate_limited_requests": rate_limited_reqs,
                    "average_latency_ms": avg_latency_ms
                },
                "endpoints": endpoints,
                "redis_statistics": redis_stats
            }
        except Exception:
            return {
                "summary": {
                    "total_requests": 0,
                    "success_requests": 0,
                    "failed_requests": 0,
                    "rate_limited_requests": 0,
                    "average_latency_ms": 0.0
                },
                "endpoints": {},
                "redis_statistics": {"status": "offline"}
            }

    async def reset(self):
        try:
            async for key in self.client.scan_iter(match="metrics:*"):
                await self.client.delete(key)
        except Exception:
            pass


metrics_service = MetricsService()