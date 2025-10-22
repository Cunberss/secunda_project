from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

from src.api.routes import api_router
from src.core.middleware import api_key_middleware

app = FastAPI(
    title="API",
    description="API",
    version="1.0.0"
)

app.middleware("http")(api_key_middleware)

# Подключаем роуты
app.include_router(api_router, prefix="/api/v1")


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description="API для справочника организаций, зданий и видов деятельности",
        routes=app.routes,
    )

    openapi_schema["components"]["securitySchemes"] = {
        "ApiKeyAuth": {
            "type": "apiKey",
            "in": "header",
            "name": "X-API-Key"
        }
    }

    for path in openapi_schema["paths"].values():
        for method in path.values():
            method["security"] = [{"ApiKeyAuth": []}]

    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi


@app.get("/")
async def root():
    return {"message": "API is running"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
