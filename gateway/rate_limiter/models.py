from dataclasses import dataclass


@dataclass
class RateLimitResult:

    allowed: bool

    remaining: int

    retry_after: int