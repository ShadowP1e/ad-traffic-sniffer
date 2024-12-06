FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    wireshark-common \
    tshark \
    libpcap-dev \
    && rm -rf /var/lib/apt/lists/*

RUN tshark -v

COPY requirements.txt /app
RUN pip install --no-cache-dir -r requirements.txt

COPY ./app /app

CMD ["python", "main.py"]
