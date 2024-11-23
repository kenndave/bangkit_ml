from fastapi.responses import JSONResponse

async def health_check():
    return JSONResponse(content={"message_code": 200, "message_description": "Service is up and running WELL", "response_data": {}})