FROM python:3.10-slim

ENV APP_HOME /app

FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .

RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1-mesa-glx \
    libglib2.0-0 \
    curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install gdown

# Download files using gdown
RUN gdown "https://drive.google.com/uc?id=17XFCjdg7g6hMB28QC_DeiresCxvhulso" -O /capstone-project-442502-e205627d1062.json \
    && gdown "https://drive.google.com/uc?id=1eIKnsBTWTSoeZQVTwAJJpr7iWJaE4DuS" -O /firebase-credential.json

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
