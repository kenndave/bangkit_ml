from fastapi import APIRouter, HTTPException, Form
from app.services.embedding_service_v1 import (
    generate_embeddings,
    create_index,
    create_index_from_csv,
)


router = APIRouter(prefix="/embeddings")


@router.post("/inference")
async def process_receipt(
    product_name: str = Form(..., description="Product's Name"),
):
    if not product_name:
        raise HTTPException(status_code=400, detail="Invalid product_name")

    try:
        response = await generate_embeddings(product_name)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


@router.get("/index")
async def process_receipt():
    try:
        response = await create_index()
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


@router.get("/index/local")
async def process_receipt():
    try:
        response = await create_index_from_csv()
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
