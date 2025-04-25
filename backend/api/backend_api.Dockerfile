FROM python:3.10-slim

WORKDIR /app

COPY . .

RUN pip install --upgrade pip && \
    pip install -r requirements.txt

EXPOSE 9001

CMD ["uvicorn", "main:app", "--port", "9001", "--host", "0.0.0.0"]
