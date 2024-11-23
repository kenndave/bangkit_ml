from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "OCR + GenAI App"
    debug: bool = False
    ocr_model_path: str = "./models"
    project_id: str = "capstone-project-442502"
    location: str = "us-central1"
    credentials: str = "capstone-project-442502-e205627d1062.json"
    database: str = "bangkit-db"
    firebase_credentials: str = "firebase-credential.json"

    class Config:
        env_file = ".env"


settings = Settings()
