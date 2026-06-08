FROM python:3.10-slim

RUN apt-get update && apt-get install -y wget unzip && \
    wget https://github.com/XTLS/Xray-core/releases/latest/download/Xray-linux-64.zip && \
    unzip Xray-linux-64.zip -d /usr/local/bin/ && \
    chmod +x /usr/local/bin/xray && \
    rm Xray-linux-64.zip

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY server.py .

CMD ["python", "server.py"]
