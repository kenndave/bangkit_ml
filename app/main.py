from fastapi import FastAPI
from routers import embedding_router_v1, receipt_router_v1
from common.config import settings
from routes.health import health_check


app = FastAPI(
    title=settings.app_name,
    description="FastAPI app for processing receipt images and generating outputs.",
    debug=settings.debug,
)




app.add_api_route("/", health_check, methods=["GET"])


# Version 1 API
app.include_router(receipt_router_v1.router, prefix="/api/v1", tags=["Receipt v1"])
app.include_router(embedding_router_v1.router, prefix="/api/v1", tags=["Embedding v1"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)