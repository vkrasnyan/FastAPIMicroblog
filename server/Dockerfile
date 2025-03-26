FROM python:3.10-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /server

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY server/ .

ENV PYTHONPATH=/server

EXPOSE 5000

CMD ["sh", "-c", "sleep 10 && uvicorn blogapp.main:app --host 0.0.0.0 --port 5000 --reload"]
