FROM python:3.12-slim

# 設定工作目錄
WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

RUN apt-get update && apt-get install -y \
    openjdk-17-jdk-headless \  
    procps \ 
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk-arm64
ENV PATH="${JAVA_HOME}/bin:${PATH}"

COPY scripts/yolo_script.py .
# COPY scripts/yolo_test.py .
COPY scripts/spark_script.py .
COPY scripts/speed_zones_config.json .
COPY scripts/yolov8s.pt .


