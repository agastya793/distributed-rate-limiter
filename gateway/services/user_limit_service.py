from gateway.services.redis_service import redis_service


class UserLimitService:
    """
    Handles client-specific rate limits, roles,
    whitelist and blacklist.
    """

    def __init__(self):
        self.client = redis_service.get_client()

    # -----------------------------
    # Custom Rate Limits
    # -----------------------------
    async def set_limit(self, client: str, limit: int):
        await self.client.set(f"rate_limit:{client}", limit)

    async def get_limit(self, client: str):
        limit = await self.client.get(f"rate_limit:{client}")

        if limit is not None:
            return int(limit)

        role = await self.get_role(client)
        return self.get_role_limit(role)

    async def remove_limit(self, client: str):
        await self.client.delete(f"rate_limit:{client}")

    async def get_all_limits(self):
        result = {}

        async for key in self.client.scan_iter(match="rate_limit:*"):
            if isinstance(key, bytes):
                key = key.decode()

            client = key.replace("rate_limit:", "")
            value = await self.client.get(key)

            if isinstance(value, bytes):
                value = value.decode()

            result[client] = int(value)

        return result

    # -----------------------------
    # Remaining Requests
    # -----------------------------
    async def get_remaining_requests(self, client: str):

        key = f"sliding:{client}"

        current_requests = await self.client.zcard(key)
        limit = await self.get_limit(client)

        return {
            "limit": limit,
            "used": current_requests,
            "remaining": max(limit - current_requests, 0)
        }

    # -----------------------------
    # Whitelist
    # -----------------------------
    async def whitelist_client(self, client: str):
        await self.client.sadd("whitelist_clients", client)

    async def is_whitelisted(self, client: str):
        return await self.client.sismember("whitelist_clients", client)

    # -----------------------------
    # Blacklist
    # -----------------------------
    async def blacklist_client(self, client: str):
        await self.client.sadd("blacklist_clients", client)

    async def is_blacklisted(self, client: str):
        return await self.client.sismember("blacklist_clients", client)

    async def remove_blacklist(self, client: str):
        await self.client.srem("blacklist_clients", client)

    # -----------------------------
    # Roles
    # -----------------------------
    async def set_role(self, client: str, role: str):
        await self.client.set(f"user_role:{client}", role)

    async def get_role(self, client: str):
        role = await self.client.get(f"user_role:{client}")

        if role is None:
            return "free"

        if isinstance(role, bytes):
            role = role.decode()

        return role

    def get_role_limit(self, role: str):

        limits = {
            "free": 10,
            "premium": 100,
            "admin": 1000000
        }

        return limits.get(role, 10)