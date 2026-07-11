from gateway.rate_limiter.algorithms import SlidingWindowAlgorithm
class RateLimiter:

    def __init__(self):

        self.algorithm = SlidingWindowAlgorithm()

    def check(self, client):

        return self.algorithm.allow_request(client)