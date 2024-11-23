import faiss
import json
import pandas as pd
import numpy as np
from google.cloud import firestore
from google.oauth2 import service_account
from app.common.logging import logger
from app.models.embedding import embedding_model
from app.common.config import settings
from app.services.receipt_service_v1 import load_faiss_and_metadata


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


async def create_index_from_csv(
    csv_file: str = "./app/files/data.csv",
    embedding_dim: int = 384,
    index_file: str = "./app/files/faiss_index.index",
    metadata_file: str = "./app/files/faiss_metadata.json",
) -> dict:
    """
    Create a FAISS index for product names from a local CSV file.

    Args:
        csv_file (str): Path to the CSV file containing product data.
        embedding_dim (int): The dimensionality of the embedding vectors.
        index_file (str): Path to save the FAISS index.
        metadata_file (str): Path to save the metadata file.

    Returns:
        dict: A dictionary containing the status and FAISS index details.
    """
    try:
        logger.info("Starting to create FAISS index from CSV...")

        # Load data from CSV
        logger.info(f"Loading data from CSV file: {csv_file}")
        df = pd.read_csv(csv_file)

        # Validate required columns
        if "product_name" not in df.columns:
            raise ValueError("CSV file must contain a 'product_name' column.")

        # Initialize FAISS index
        index = faiss.IndexFlatL2(embedding_dim)
        product_metadata = {}

        # Iterate through the CSV rows
        for idx, row in df.iterrows():
            product_name = row["product_name"]
            product_id = row["product_id"]
            price = row["price"]

            # Skip rows without product_name
            if not product_name or pd.isna(product_name):
                logger.warning(f"Skipping row {idx} with missing product_name.")
                continue

            # Generate embedding
            embeddings = embedding_model.embed_query(product_name)
            embeddings = np.array(embeddings).reshape(
                1, -1
            )  # Ensure embeddings are a NumPy array

            # Add embedding to FAISS index
            index.add(embeddings)
            product_metadata[idx] = {
                "product_id": product_id,
                "product_name": product_name,
                "price": price,
            }

        # Save FAISS index locally
        faiss.write_index(index, index_file)
        logger.info(f"FAISS index created and saved to {index_file}")

        # Save metadata locally
        with open(metadata_file, "w") as f:
            json.dump(product_metadata, f, indent=4)
        logger.info(f"Metadata saved to {metadata_file}")
        load_faiss_and_metadata()

        # Return success response
        return {
            "status": "success",
            "message": "FAISS index and metadata created successfully from CSV",
            "data": {
                "index_file": index_file,
                "metadata_file": metadata_file,
                "num_embeddings": index.ntotal,
            },
        }

    except Exception as e:
        logger.error(f"Error creating FAISS index from CSV: {e}")
        return {
            "status": "failed",
            "message": "Failed to create FAISS index. Please try again.",
            "data": None,
        }


async def create_index(
    collection_name: str = "products",
    embedding_dim: int = 384,
    index_file: str = "./app/files/faiss_index.index",
    metadata_file: str = "./app/files/faiss_metadata.json",
) -> dict:
    """
    Create a FAISS index for product names from Firestore.

    Args:
        collection_name (str): The Firestore collection containing product data.
        embedding_dim (int): The dimensionality of the embedding vectors.
        index_file (str): Path to save the FAISS index.
        metadata_file (str): Path to save the metadata file.

    Returns:
        dict: A dictionary containing the status and FAISS index details.
    """
    try:
        logger.info("Starting to create FAISS index...")

        # Initialize Firestore client
        credentials = service_account.Credentials.from_service_account_file(
            settings.firebase_credentials
        )
        firestore_client = firestore.Client(
            project=settings.project_id,
            database=settings.database,
            credentials=credentials,
        )

        # Fetch product data from Firestore
        logger.info(f"Fetching data from Firestore collection: {collection_name}")
        docs = firestore_client.collection(collection_name).stream()

        # Initialize FAISS index
        index = faiss.IndexFlatL2(embedding_dim)
        product_metadata = {}

        for idx, doc in enumerate(docs):
            data = doc.to_dict()
            product_id = data.get("product_id", "")
            product_name = data.get("product_name", "")
            price = data.get("price", "")
            if not product_name:
                logger.warning(f"Skipping document {doc.id} with no product_name")
                continue

            # Generate embedding
            embeddings = embedding_model.embed_query(product_name)
            embeddings = np.array(embeddings).reshape(
                1, -1
            )

            # Add embedding to FAISS index
            index.add(embeddings.reshape(1, -1))
            product_metadata[idx] = {"product_id": product_id, "product_name": product_name, "price": price}

        # Save FAISS index locally
        faiss.write_index(index, index_file)
        logger.info(f"FAISS index created and saved to {index_file}")

        # Save metadata locally
        with open(metadata_file, "w") as f:
            json.dump(product_metadata, f, indent=4)
        logger.info(f"Metadata saved to {metadata_file}")
        load_faiss_and_metadata()

        # Return success response
        return {
            "status": "success",
            "message": "FAISS index and metadata created successfully",
            "data": {
                "index_file": index_file,
                "metadata_file": metadata_file,
                "num_embeddings": index.ntotal,
            },
        }

    except Exception as e:
        logger.error(f"Error creating FAISS index: {e}")
        return {
            "status": "failed",
            "message": "Failed to create FAISS index. Please try again.",
            "data": None,
        }
