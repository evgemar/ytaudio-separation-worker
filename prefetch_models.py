"""Download the default Mel-Band Roformer checkpoint at image-build time."""
import logging

from audio_separator.separator import Separator

logging.getLogger().setLevel(logging.WARNING)

print("Downloading Mel-Band Roformer model...")
separator = Separator()
separator.load_model(model_filename="model_bs_roformer_ep_317_sdr_12.9755.ckpt")
print("Model download complete")
