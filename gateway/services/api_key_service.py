import secrets

from gateway.services.redis_service import redis_service


class APIKeyService:

    def __init__(self):
        self.client = redis_service.get_client()

    # -------------------------
    # Generate API Key
    # -------------------------
    async def generate_api_key(self, client: str):
        api_key = secrets.token_hex(32)

        await self.client.set(
            f"api_key:{api_key}",
            client
        )

        return api_key

    # -------------------------
    # Validate API Key
    # -------------------------
    async def validate_api_key(self, api_key: str):

        client = await self.client.get(f"api_key:{api_key}")

        if client is None:
            return None

        if isinstance(client, bytes):
            client = client.decode()

        return client

    # -------------------------
    # Revoke API Key
    # -------------------------
    async def revoke_api_key(self, api_key: str):
        await self.client.delete(f"api_key:{api_key}")