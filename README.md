# OCR + GenAI App

A FastAPI-based application for processing receipt images using PaddleOCR and generating structured data for further analysis. The application leverages PaddleOCR for Optical Character Recognition (OCR) and supports GPU acceleration for enhanced performance.

## Features

- **Preprocessing**:
  - Includes image preprocessing for better OCR results.
- **OCR with PaddleOCR**:
  - Processes receipt images to extract text.
- **Structured Data Output with GenAI**:
  - Returns structured data with user information, itemized receipts, and total price.

## Requirements

- **Python**: 3.10 or later
- **Docker** (optional): For containerized deployment
- **GPU Support** (optional): NVIDIA CUDA 11.8 or later for GPU acceleration

## Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/MarcelRyan/Bangkit_OCR.git
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```


## Running the Application

### 1. Run the app without Docker
```bash
python run.py
```
### 2. Run the app with Docker
```bash
docker-compose build
docker-compose up
```
