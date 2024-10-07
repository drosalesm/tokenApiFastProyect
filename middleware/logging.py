# middleware/logging_middleware.py
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
import logging
import uuid
from db.database import SessionLocal
from models.models import Logs  # Adjust this import according to your project structure



logger = logging.getLogger(__name__)

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = str(uuid.uuid4())
        logger.info(f"Request ID: {request_id} - Method: {request.method} - Path: {request.url.path}")
        
        body = await request.body()
        logger.info(f"Request Body: {body.decode('utf-8')}")

        response: Response = await call_next(request)
        logger.info(f"Request ID: {request_id} - Status Code: {response.status_code}")

        self.log_to_database(request_id, request.method, request.url.path, body.decode('utf-8'), response.status_code)

        return response

