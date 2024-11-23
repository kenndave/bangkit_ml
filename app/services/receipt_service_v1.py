from paddleocr import PaddleOCR
from PIL import Image
import io
from datetime import datetime
from fastapi import UploadFile
from app.common.logging import logger
from app.utils.image_utils import preprocess_image
from app.utils.llm_utils import fix_typos_and_parse
from app.utils.timestamp_utils import is_valid_timestamp


ocr = PaddleOCR(use_angle_cls=True, lang="en")


async def process_receipt_image(image: UploadFile, user_id: str) -> dict:
    try:
        logger.info("Starting receipt processing...")

        # Step 1: Read the uploaded image
        logger.info("Reading the uploaded image.")
        contents = await image.read()
        pil_image = Image.open(io.BytesIO(contents)).convert("RGB")
        logger.info("Image successfully loaded into PIL.")

        # Step 2: Preprocess the image
        logger.info("Preprocessing the image.")
        numpy_image = preprocess_image(pil_image)
        logger.info("Image preprocessing completed.")

        # Step 3: Perform OCR
        logger.info("Running OCR on the preprocessed image.")
        results = ocr.ocr(numpy_image, cls=True)
        logger.info("OCR processing completed.")

        # Step 4: Extract text from OCR results
        logger.info("Extracting text from OCR results.")
        extracted_text = []
        for line in results[0]:
            extracted_text.append(line[1][0])
        logger.info(f"Extracted text: {extracted_text}")

        # Step 5: Fix typos and parse text with gemini
        logger.info("Fixing typos and parsing text with gemini.")
        structured_data = fix_typos_and_parse(extracted_text)
        logger.info(f"Structured data: {structured_data}")

        # Step 6: Create JSON response
        timestamp = structured_data["timestamp"]
        if is_valid_timestamp(timestamp):
            data = {
                "user_id": user_id,
                "timestamp": timestamp,
                "items": structured_data["items"],
                "total_price": structured_data.get("total_price", None),
            }
        else:
            # Use current time if the timestamp is invalid
            data = {
                "user_id": user_id,
                "timestamp": datetime.now().isoformat(),
                "items": structured_data["items"],
                "total_price": structured_data.get("total_price", None),
            }
        logger.info("Receipt data successfully created.")

        # TODO: Vector Search for Validate Products

        # Return success response
        logger.info(f"Receipt processed successfully for user_id: {user_id}")
        return {
            "status": "success",
            "message": "Receipt processed successfully",
            "data": data,
        }

    except Exception as e:
        logger.error(f"Error processing receipt: {e}")
        return {
            "status": "failed",
            "message": "Failed to process receipt. Please try again.",
            "data": None,
        }
