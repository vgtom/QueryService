import logging
import json
from datetime import datetime
from typing import Any, Dict
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
import structlog

# Configure structlog
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.PrintLoggerFactory(),
    wrapper_class=structlog.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = datetime.utcnow()
        
        # Extract request details
        request_id = request.headers.get("X-Request-ID", "")
        
        # Log request
        logger.info(
            "incoming_request",
            request_id=request_id,
            method=request.method,
            url=str(request.url),
            client_ip=request.client.host,
        )
        
        try:
            response = await call_next(request)
            
            # Log response
            logger.info(
                "outgoing_response",
                request_id=request_id,
                status_code=response.status_code,
                duration_ms=(datetime.utcnow() - start_time).total_seconds() * 1000,
            )
            
            return response
        except Exception as e:
            # Log error
            logger.error(
                "request_failed",
                request_id=request_id,
                error=str(e),
                duration_ms=(datetime.utcnow() - start_time).total_seconds() * 1000,
            )
            raise 