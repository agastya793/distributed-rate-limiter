from pydantic import BaseModel


class RateLimitRequest(BaseModel):
    client: str
    limit: int

class UserRoleRequest(BaseModel):
    client: str
    role: str   

