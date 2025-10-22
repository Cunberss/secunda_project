from fastapi import Request
from fastapi.responses import JSONResponse

from src.core import settings


async def api_key_middleware(request: Request, call_next):
    if request.url.path.startswith("/docs") or request.url.path.startswith("/openapi"):
        return await call_next(request)

    x_api_key = request.headers.get("x-api-key")
    if x_api_key != settings.api_key:
        return JSONResponse(status_code=401, content={"detail": "Invalid API Key"})

    return await call_next(request)
