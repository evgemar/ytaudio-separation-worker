import runpod
import base64
import tempfile
import os
from audio_separator.separator import Separator
from pathlib import Path
import logging
import subprocess

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Default model - Mel-Band Roformer vocals checkpoint
DEFAULT_MODEL = "model_bs_roformer_ep_317_sdr_12.9755.ckpt"

def download_audio_from_url(url, output_path):
    """Download audio from URL using ffmpeg"""
    try:
        subprocess.run([
            'ffmpeg', '-i', url, '-y',
            '-ar', '44100', '-ac', '2',  # 44.1kHz stereo for separation
            '-f', 'wav', output_path
        ], check=True, capture_output=True)
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to download audio: {e}")
        return False

def convert_to_wav(audio_data, output_path):
    """Convert audio data to WAV format using ffmpeg"""
    try:
        with tempfile.NamedTemporaryFile(delete=False) as temp_input:
            temp_input.write(audio_data)
            temp_input.flush()

            subprocess.run([
                'ffmpeg', '-i', temp_input.name, '-y',
                '-ar', '44100', '-ac', '2',  # 44.1kHz stereo for separation
                '-f', 'wav', output_path
            ], check=True, capture_output=True)

        os.unlink(temp_input.name)
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to convert audio: {e}")
        return False

def separate_audio(input_path, model_name=DEFAULT_MODEL):
    """Separate vocals and background using audio-separator"""
    try:
        # Initialize separator
        separator = Separator()

        # Load model (use GPU if available)
        separator.load_model(model_filename=model_name)

        # Create output directory
        output_dir = tempfile.mkdtemp()

        # Perform separation - returns list of output files
        outputs = separator.separate(input_path, output_dir=output_dir)

        # Find vocals and background files
        vocals_path = None
        background_path = None

        for output_file in outputs:
            filename = Path(output_file).name.lower()
            if 'vocal' in filename:
                vocals_path = output_file
            elif 'background' in filename or 'instrument' in filename or 'music' in filename:
                background_path = output_file

        if not vocals_path or not background_path:
            raise ValueError("Could not find both vocals and background outputs")

        return vocals_path, background_path, output_dir

    except Exception as e:
        logger.error(f"Separation failed: {e}")
        raise

def handler(job):
    """RunPod handler for audio separation"""
    try:
        job_input = job["input"]

        # Get model (optional)
        model = job_input.get("model", DEFAULT_MODEL)
        logger.info(f"Using separation model: {model}")

        # Create temp directory for this job
        with tempfile.TemporaryDirectory() as temp_dir:
            input_audio_path = os.path.join(temp_dir, "input.wav")

            # Handle audio input - either base64 or URL
            if "audio_base64" in job_input:
                logger.info("Processing base64 audio input")
                audio_data = base64.b64decode(job_input["audio_base64"])
                if not convert_to_wav(audio_data, input_audio_path):
                    return {"error": "Failed to convert input audio"}

            elif "audio_url" in job_input:
                logger.info(f"Processing URL audio input: {job_input['audio_url']}")
                if not download_audio_from_url(job_input["audio_url"], input_audio_path):
                    return {"error": "Failed to download audio from URL"}

            else:
                return {"error": "Missing required input: audio_base64 or audio_url"}

            # Perform separation
            logger.info("Starting audio separation")
            vocals_path, background_path, output_dir = separate_audio(input_audio_path, model)

            # Read output files and convert to base64
            with open(vocals_path, 'rb') as f:
                vocals_base64 = base64.b64encode(f.read()).decode('utf-8')

            with open(background_path, 'rb') as f:
                background_base64 = base64.b64encode(f.read()).decode('utf-8')

            # Clean up output directory
            import shutil
            shutil.rmtree(output_dir, ignore_errors=True)

            logger.info("Separation completed successfully")
            return {
                "vocals_base64": vocals_base64,
                "background_base64": background_base64,
                "model_used": model
            }

    except Exception as e:
        logger.error(f"Handler error: {e}")
        return {"error": str(e)}

# RunPod serverless handler
runpod.serverless.start({"handler": handler})