FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# 创建必要的目录（用于挂载）
RUN mkdir -p /data /downloads /cbz

ENV PYTHONUNBUFFERED=1
ENV CMNAS_DATA_PATH=/data
ENV CMNAS_DOWNLOAD_PATH=/downloads
ENV CMNAS_CBZ_PATH=/cbz

EXPOSE 8000

CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]