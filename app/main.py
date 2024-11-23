from fastapi import FastAPI
from app.routers import embedding_router_v1, receipt_router_v1
from app.common.config import settings
from app.common.logging import logger

app = FastAPI(
    title=settings.app_name,
    description="FastAPI app for processing receipt images and generating outputs.",
    debug=settings.debug,
)

logger.info(f"Starting {settings.app_name}")


@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "OK", "message": f"{settings.app_name} is running"}


# Version 1 API
app.include_router(receipt_router_v1.router, prefix="/api/v1", tags=["Receipt v1"])
app.include_router(embedding_router_v1.router, prefix="/api/v1", tags=["Embedding v1"])
