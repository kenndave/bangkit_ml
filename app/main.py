from fastapi import FastAPI
from app.routers import embedding_router_v1, receipt_router_v1
# from app.common.config import settings
# from app.common.logging import logger
from routes.health import health_check
import os

APP_NAME = os.getenv("APP_NAME", "OCR + GenAI App")
DEBUG = os.getenv("DEBUG", "false").lower() == "true"  # Convert string to boolean
# DESCRIPTION = os.getenv(
#     "APP_DESCRIPTION", "FastAPI app for processing receipt images and generating outputs."
# )
app = FastAPI(
    title=APP_NAME,
    description="FastAPI app for processing receipt images and generating outputs.",
    debug=DEBUG,
)

# logger.info(f"Starting {settings.app_name}")


app.add_api_route("/", health_check, methods=["GET"])


# Version 1 API
app.include_router(receipt_router_v1.router, prefix="/api/v1", tags=["Receipt v1"])
app.include_router(embedding_router_v1.router, prefix="/api/v1", tags=["Embedding v1"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)