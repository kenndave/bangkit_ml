from datetime import datetime

def is_valid_timestamp(timestamp) -> bool:
    """
    Validates if the given timestamp is in ISO 8601 format.
    
    Args:
        timestamp (str): The timestamp string to validate.
    
    Returns:
        bool: True if the timestamp is valid, False otherwise.
    """
    try:
        if timestamp == None:
            return False

        # Try to parse the timestamp in ISO 8601 format
        datetime.fromisoformat(timestamp)
        return True
    except ValueError:
        return False