FROM pytorch/pytorch:2.4.0-cuda12.1-cudnn8-runtime

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Prefetch default models during build (on CPU to save time)
RUN python -c "
from audio_separator.separator import Separator
import logging
logging.getLogger().setLevel(logging.WARNING)
print('Downloading Mel-Band Roformer model...')
separator = Separator()
separator.load_model(model_filename='model_bs_roformer_ep_317_sdr_12.9755.ckpt')
print('Model download complete')
"

# Copy handler
COPY rp_handler.py .

# Run handler
CMD ["python", "rp_handler.py"]