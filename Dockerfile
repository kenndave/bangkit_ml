FROM python:3.10-slim

ENV APP_HOME /app

WORKDIR $APP_HOME

COPY requirements.txt ./

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8080

CMD ["python", "app/main.py"]
