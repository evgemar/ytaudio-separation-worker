FROM pytorch/pytorch:2.4.0-cuda12.1-cudnn8-devel

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    wget \
    git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY prefetch_models.py .
RUN python prefetch_models.py

COPY rp_handler.py .

CMD ["python", "rp_handler.py"]
