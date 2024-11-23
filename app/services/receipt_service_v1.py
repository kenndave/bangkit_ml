import io
import faiss
import json
import numpy as np
from paddleocr import PaddleOCR
from PIL import Image
from datetime import datetime
from fastapi import UploadFile
from app.common.logging import logger
from app.utils.image_utils import preprocess_image
from app.utils.llm_utils import fix_typos_and_parse
from app.utils.timestamp_utils import is_valid_timestamp
from app.models.embedding import embedding_model

# Constants for file paths
FAISS_INDEX_FILE = "./app/files/faiss_index.index"
PRODUCT_METADATA_FILE = "./app/files/faiss_metadata.json"
PRETRAINED_FILE = "./app/files/en_number_mobile_v2.0_rec_train/"

# Load models and data
ocr = PaddleOCR(use_angle_cls=True, lang="en", rec_model_dir=PRETRAINED_FILE)
faiss_index = None
product_metadata = {}


def load_faiss_and_metadata():
    """Load FAISS index and metadata."""
    global faiss_index, product_metadata
    try:
        # Load FAISS index
        faiss_index = faiss.read_index(FAISS_INDEX_FILE)
        logger.info("FAISS index loaded successfully.")

        # Load metadata
        with open(PRODUCT_METADATA_FILE, "r") as f:
            product_metadata = json.load(f)
        logger.info("Product metadata loaded successfully.")
    except FileNotFoundError as e:
        logger.error(f"File not found: {e}")
    except Exception as e:
        logger.error(f"Error loading FAISS index or metadata: {e}")


# Initialize FAISS and metadata
load_faiss_and_metadata()


async def process_receipt_image(image: UploadFile, user_id: str) -> dict:
    """
    Process the receipt image and validate product information using FAISS.
    Args:
        image (UploadFile): Uploaded receipt image.
        user_id (str): User identifier.
    Returns:
        dict: Processed receipt data with validation status.
    """
    try:
        logger.info("Starting receipt processing...")

        # Step 1: Read and preprocess image
        pil_image = await load_and_preprocess_image(image)

        # Step 2: Perform OCR and extract text
        extracted_text = perform_ocr(pil_image)

        # Step 3: Fix typos and parse extracted text
        products = [product["product_name"] for product in product_metadata.values()]
        structured_data = fix_typos_and_parse(extracted_text, products)
        data = prepare_initial_data(structured_data, user_id)

        # Step 4: Validate products using FAISS vector search
        data = validate_products_with_faiss(data)

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


async def load_and_preprocess_image(image: UploadFile) -> Image:
    """Read and preprocess the uploaded image."""
    logger.info("Reading and preprocessing the uploaded image.")
    contents = await image.read()
    pil_image = Image.open(io.BytesIO(contents)).convert("RGB")
    numpy_image = preprocess_image(pil_image)
    logger.info("Image preprocessing completed.")
    return numpy_image


def perform_ocr(image) -> list:
    """Perform OCR on the preprocessed image."""
    logger.info("Running OCR on the preprocessed image.")
    results = ocr.ocr(image, cls=True)
    extracted_text = [line[1][0] for line in results[0]]
    logger.info(f"Extracted text: {extracted_text}")
    return extracted_text


def prepare_initial_data(structured_data: dict, user_id: str) -> dict:
    """Prepare the initial receipt data structure."""
    timestamp = structured_data.get("timestamp", datetime.now().isoformat())
    if not is_valid_timestamp(timestamp):
        timestamp = datetime.now().isoformat()
    data = {
        "user_id": user_id,
        "timestamp": timestamp,
        "items": structured_data.get("items", []),
        "total_price": structured_data.get("total_price", 0),
    }
    logger.info("Initial receipt data prepared.")
    return data


def validate_products_with_faiss(data: dict) -> dict:
    """Validate product information using FAISS vector search."""
    if not faiss_index or not product_metadata:
        logger.warning("FAISS index or metadata not loaded. Skipping validation.")
        return data

    logger.info("Validating products using FAISS vector search.")
    valid_items = []
    total_price = 0

    for item in data["items"]:
        product_name = item["product_name"]
        embedding = np.array(embedding_model.embed_query(product_name)).reshape(1, -1)

        # Perform FAISS search
        distances, indices = faiss_index.search(embedding, k=1)
        if distances[0][0] < 1:  # Match threshold
            matched_product = product_metadata[str(indices[0][0])]
            item.update(
                {
                    "product_id": matched_product["product_id"],
                    "product_name": matched_product["product_name"],
                    "price_per_unit": float(matched_product["price"]),
                    "total_price": float(matched_product["price"])
                    * float(item["quantity"]),
                }
            )
            total_price += float(item["total_price"])
            valid_items.append(item)
        else:
            logger.warning(
                f"Product {product_name} has no similar match and was removed."
            )

    data["items"] = valid_items
    data["total_price"] = total_price
    logger.info("Product validation completed.")
    return data
