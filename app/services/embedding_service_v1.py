from app.common.logging import logger
from app.models.embedding import embedding_model

async def generate_embeddings(product_name: str) -> dict:
    """
    Generate embeddings for the given product name using HuggingFaceEmbeddings.

    Args:
        product_name (str): The product name for which embeddings are generated.

    Returns:
        dict: A dictionary containing the status, message, and generated embeddings.
    """
    try:
        logger.info("Starting to generate embeddings...")

        # Generate embeddings using the model
        embeddings = embedding_model.embed_query(product_name)

        # Log success
        logger.info(f"Processed successfully for product_name: {product_name}")

        # Return success response
        return {
            "status": "success",
            "message": "Embeddings generated successfully",
            "data": {"product_name": product_name, "embeddings": embeddings},
        }

    except Exception as e:
        logger.error(f"Error generating embeddings: {e}")
        return {
            "status": "failed",
            "message": "Failed to generate embeddings. Please try again.",
            "data": None,
        }
