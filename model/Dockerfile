FROM python:3.11

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY model/ /app/model/

WORKDIR /app/model

CMD ["python", "run_e2e_validation.py"]
