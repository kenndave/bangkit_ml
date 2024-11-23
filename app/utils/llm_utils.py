from typing import List, Dict
import json
from app.models.llm import VertexAILLM

gemini_llm = VertexAILLM()


def fix_typos_and_parse(extracted_text: List[str], products: list) -> Dict:
    """
    Fix typos in extracted text and parse it into structured data using Gemini.
    """
    # Create product context
    product_context = ",".join(products)

    # Create a refined prompt
    prompt = f"""
    You are an advanced AI assistant tasked with processing OCR text from a receipt. Your goal is to extract structured data with the following requirements:

    Here is the list of products available in the store:
    {product_context}

    Input:
    {extracted_text}

    Tasks:
    1. Correct any typos in product names.
    2. Parse the information into a JSON object with the following structure:
       {{
           "timestamp": "<timestamp in ISO 8601 format (YYYY-MM-DDTHH:MM:SS)>",
           "items": [
               {{
                   "product_name": "<corrected product name>",
                   "quantity": <integer quantity>,
                   "price_per_unit": 0,
                   "total_price": 0
               }}
           ],
           "total_price": 0
       }}
    3. Extract only the product name, quantity, and timestamp (if present) from the OCR text.
    4. If a timestamp exists, convert it to ISO 8601 format (YYYY-MM-DDTHH:MM:SS). If no timestamp is found, set "timestamp" to null.
    5. Leave "price_per_unit" and "total_price" as 0 for all items.
    6. If quantity is a large number, change it to 0.

    Additional Notes:
    - Use double quotes (") for all property names and string values to ensure the response is valid JSON.
    - Ensure all numbers (e.g., quantity) are represented as integers, not strings.
    - Return only the JSON response, strictly adhering to the specified format.
    - Do not include any additional text or comments in the output.

    Example Output:
    {{
        "timestamp": "2024-11-23T12:41:30",
        "items": [
            {{
                "product_name": "Apple",
                "quantity": 2,
                "price_per_unit": 0,
                "total_price": 0
            }},
            {{
                "product_name": "Orange",
                "quantity": 1,
                "price_per_unit": 0,
                "total_price": 0
            }}
        ],
        "total_price": 0
    }}
    """

    response = gemini_llm.generate(prompt)
    try:
        # Extract the JSON part from the response
        start_idx = response.find("{")
        end_idx = response.rfind("}") + 1
        if start_idx == -1 or end_idx == 0:
            raise ValueError("No JSON object found in the response.")

        json_response = json.loads(response[start_idx:end_idx])
        return json_response
    except json.JSONDecodeError as e:
        raise ValueError(f"Error parsing JSON response from Gemini: {e}")
    except Exception as e:
        raise ValueError(f"Unexpected error occurred: {e}")
