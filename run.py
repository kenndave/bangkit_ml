import os
from dotenv import load_dotenv
import subprocess

if os.path.exists(".env"):
    print("Loading environment variables from .env...")
    load_dotenv(dotenv_path=".env")
else:
    print(".env file not found. Please create one.")
    exit(1)

print("Starting FastAPI application...")
subprocess.run(
    ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"],
    check=True,
)
