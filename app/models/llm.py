import vertexai
from vertexai.generative_models import GenerativeModel
from ..common.config import settings
from ..common.logging import logger
from google.auth.transport.requests import Request
from google.oauth2.service_account import Credentials

class VertexAILLM():
    """
    A wrapper for Google Cloud's Vertex AI model.
    """

    def __init__(
        self,
        model_name: str = "gemini-1.5-flash-002",
    ):
        # Attributes
        self.model_name = model_name

        credentials = Credentials.from_service_account_file(
            settings.credentials,
            scopes=['https://www.googleapis.com/auth/cloud-platform'])

        if credentials.expired:
            credentials.refresh(Request())

        vertexai.init(project=settings.project_id, location=settings.location, credentials=credentials)

    @property
    def _llm_type(self) -> str:
        return "vertex-ai-gemini"

    def generate(self, prompt: str) -> str:
        """
        Call the Vertex AI Gemini model with the given prompt.
        """
        try:
            # Load the model
            model = GenerativeModel(self.model_name)

            # Generate the response
            response = model.generate_content(prompt)
            logger.info(response.text)

            return response.text
        except Exception as e:
            raise ValueError(f"Error during Vertex AI Gemini processing: {e}")
