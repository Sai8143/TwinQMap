import time
from fastapi import Request, Response, status
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Dict, Tuple

class SimpleRateLimiterMiddleware(BaseHTTPMiddleware):
    """
    Rate Limiting Middleware restricting client requests per minute.
    """

    def __init__(self, app, limit: int = 100, window_seconds: int = 60):
        super().__init__(app)
        self.limit = limit
        self.window = window_seconds
        # Store requests as (client_ip) -> list of timestamps
        self.requests: Dict[str, list] = {}

    async def dispatch(self, request: Request, call_next) -> Response:
        client_ip = request.client.host if request.client else "unknown_ip"
        current_time = time.time()

        # Clean old timestamps
        if client_ip not in self.requests:
            self.requests[client_ip] = []
        
        timestamps = self.requests[client_ip]
        self.requests[client_ip] = [t for t in timestamps if current_time - t < self.window]

        if len(self.requests[client_ip]) >= self.limit:
            return Response(
                content="API Rate Limit Exceeded. Please slow down request calls.",
                status_code=status.HTTP_429_TOO_MANY_REQUESTS
            )

        self.requests[client_ip].append(current_time)
        return await call_next(request)
