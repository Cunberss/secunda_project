from fastapi import FastAPI
from src.api.routes import api_router


app = FastAPI(
    title="API",
    description="API",
    version="1.0.0"
)

# Подключаем роуты
app.include_router(api_router, prefix="/api/v1")


@app.on_event("startup")
async def startup_event():
    pass


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
