# RunPod Audio Separation Worker

High-quality vocal/background separation using Mel-Band Roformer via `nomadkaraoke/python-audio-separator`.

## Features

- **Mel-Band Roformer**: State-of-the-art separation model (SDR 11.6-11.94)
- **GPU Acceleration**: CUDA-optimized for fast processing
- **Flexible Input**: Supports both base64 audio and URL downloads
- **Pre-cached Models**: Models downloaded at build time for faster cold starts

## Deployment

### 1. Build Image

```bash
# From this directory
docker build -t audio-separation-worker .
```

### 2. Push to Registry

```bash
# Tag for your registry
docker tag audio-separation-worker your-registry/audio-separation-worker:latest
docker push your-registry/audio-separation-worker:latest
```

### 3. Deploy on RunPod

1. Go to [RunPod Serverless](https://runpod.io/serverless)
2. Create new endpoint
3. Configure:
   - **Image**: `your-registry/audio-separation-worker:latest`
   - **GPU**: RTX 4090 or better (24GB+ VRAM recommended)
   - **Container Disk**: 20GB (for model storage)
   - **CPU**: 8+ cores, 32GB+ RAM

### 4. Environment Variables

Set in your main application:

```bash
SEPARATION_RUNPOD_ENDPOINT_ID=your-endpoint-id
SEPARATION_BASE_URL=https://api.runpod.ai/v2/your-endpoint-id
RUNPOD_API_KEY=your-api-key
```

## API Usage

### Input Format

```json
{
  "input": {
    "audio_base64": "base64-encoded-audio-data",
    "model": "model_bs_roformer_ep_317_sdr_12.9755.ckpt"
  }
}
```

Or with URL:

```json
{
  "input": {
    "audio_url": "https://example.com/audio.wav",
    "model": "model_bs_roformer_ep_317_sdr_12.9755.ckpt"
  }
}
```

### Output Format

```json
{
  "vocals_base64": "base64-encoded-vocals-wav",
  "background_base64": "base64-encoded-background-wav",
  "model_used": "model_bs_roformer_ep_317_sdr_12.9755.ckpt"
}
```

## Models

Default model: `model_bs_roformer_ep_317_sdr_12.9755.ckpt` (Mel-Band Roformer)

Alternative models available:
- `UVR-MDX-NET-Inst_HQ_3.onnx`
- `htdemucs_ft.yaml`
- `htdemucs.yaml`

## Performance

- **Cold start**: ~30-45s (model loading)
- **Warm processing**: ~2-5s per minute of audio
- **Memory**: 8-12GB VRAM for typical songs
- **Quality**: SDR 11.6+ on standard test sets
