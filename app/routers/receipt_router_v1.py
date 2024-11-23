from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from app.services.receipt_service_v1 import process_receipt_image

router = APIRouter(prefix="/receipt")


@router.post("/inference")
async def process_receipt(
    user_id: str = Form(..., description="User ID associated with the receipt"),
    image: UploadFile = File(..., description="Image file of the receipt"),
):
    if not image.content_type.startswith("image/"):
        raise HTTPException(
            status_code=400, detail="Invalid file type. Please upload an image."
        )
    if not user_id:
        raise HTTPException(status_code=400, detail="Invalid user_id")

    try:
        response = await process_receipt_image(image, user_id)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
