from PIL import Image, ImageEnhance
import numpy as np


def preprocess_image(pil_image: Image, max_size: int = 1024) -> np.ndarray:
    """
    Preprocess the image by resizing and converting to grayscale.
    Args:
        pil_image (Image): PIL image to preprocess.
        max_size (int): Maximum size for width or height to maintain aspect ratio.

    Returns:
        np.ndarray: Preprocessed image as a numpy array.
    """
    pil_image.thumbnail((max_size, max_size))

    enhancer = ImageEnhance.Contrast(pil_image)
    pil_image = enhancer.enhance(2.0)

    pil_image = pil_image.convert("L")

    numpy_image = np.array(pil_image)
    return numpy_image
