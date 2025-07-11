#!/usr/bin/env python3
"""
Simple TTS Implementation for Unicorn Aware
Uses kokoro-onnx with HuggingFace magicunicorn/kokoro-npu-quantized models
"""

import logging
import os
import sys
from typing import Optional
from pathlib import Path
import requests
from huggingface_hub import hf_hub_download
import tempfile

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')
logger = logging.getLogger(__name__)

# Local NPU model configuration
LOCAL_NPU_MODEL_DIR = "/home/ucadmin/Development/kokoro_npu_project/optimized_models"
FALLBACK_MODEL_DIR = "/home/ucadmin/Development/kokoro_npu_project"

# HuggingFace model configuration (fallback)
HF_REPO = "magicunicorn/kokoro-npu-quantized"
MODEL_FILES = {
    "kokoro-npu-quantized-int8.onnx": "kokoro-npu-quantized-int8.onnx",
    "kokoro-npu-quantized-fp16.onnx": "kokoro-npu-quantized-fp16.onnx", 
    "voices-v1.0.bin": "voices-v1.0.bin"
}

# Try to import your NPU-optimized Kokoro implementation first
try:
    from .kokoro_mlir_integration import KokoroMLIRNPUIntegration, create_kokoro_mlir_npu_integration
    KOKORO_NPU_AVAILABLE = True
    logger.info("✅ Kokoro NPU MLIR integration available")
except ImportError as e:
    KOKORO_NPU_AVAILABLE = False
    logger.warning(f"⚠️ Kokoro NPU MLIR integration not available: {e}")

# Try to import legacy unicorn_execution_engine if it exists
try:
    from unicorn_execution_engine import UnicornTTS
    UNICORN_TTS_AVAILABLE = True
    logger.info("✅ UnicornTTS NPU engine available")
except ImportError as e:
    UNICORN_TTS_AVAILABLE = False
    logger.warning(f"⚠️ UnicornTTS NPU engine not available: {e}")

# Import from the NPU-optimized kokoro-onnx package
try:
    # Add the NPU-optimized kokoro-onnx package to path
    kokoro_npu_path = "/home/ucadmin/Development/kokoro_npu_project/kokoro-onnx/src"
    if kokoro_npu_path not in sys.path:
        sys.path.insert(0, kokoro_npu_path)
    
    from kokoro_onnx import Kokoro
    KOKORO_AVAILABLE = True
    logger.info("✅ NPU-optimized Kokoro ONNX available")
except ImportError as e:
    # Fallback to standard kokoro-onnx
    try:
        from kokoro_onnx import Kokoro
        KOKORO_AVAILABLE = True
        logger.info("✅ Standard Kokoro ONNX available")
    except ImportError as e2:
        KOKORO_AVAILABLE = False
        logger.warning(f"⚠️ Kokoro ONNX not available: {e2}")

# Create fallback classes
class FallbackKokoro:
    def __init__(self, model_path=None, voices_path=None):
        self.model_path = model_path
        self.voices_path = voices_path
    
    def create_audio(self, text: str, voice: str = "af_bella") -> bytes:
        logger.warning("TTS fallback: creating silence")
        return b""
    
    def save_audio(self, audio: bytes, filename: str):
        logger.warning(f"TTS fallback: would save to {filename}")

class FallbackUnicornTTS:
    def __init__(self, model="kokoro-npu-quantized"):
        self.model = model
    
    def synthesize(self, text: str) -> bytes:
        logger.warning("NPU TTS fallback: creating silence")
        return b""

# Set up classes based on availability
if not UNICORN_TTS_AVAILABLE:
    UnicornTTS = FallbackUnicornTTS

if not KOKORO_AVAILABLE:
    Kokoro = FallbackKokoro

def download_model_file(filename: str, cache_dir: str = None) -> str:
    """Download model file from HuggingFace"""
    try:
        if cache_dir is None:
            cache_dir = os.path.join(os.path.expanduser("~"), ".cache", "unicorn-aware", "tts")
        
        os.makedirs(cache_dir, exist_ok=True)
        
        # Check if file already exists
        local_path = os.path.join(cache_dir, filename)
        if os.path.exists(local_path):
            logger.info(f"✅ Using cached model: {filename}")
            return local_path
        
        logger.info(f"📥 Downloading {filename} from HuggingFace...")
        
        # Download from HuggingFace with LFS support
        downloaded_path = hf_hub_download(
            repo_id=HF_REPO,
            filename=filename,
            cache_dir=cache_dir,
            force_download=True,  # Force download to get actual files
            local_files_only=False,
            repo_type="model"
        )
        
        logger.info(f"✅ Downloaded: {filename}")
        return downloaded_path
        
    except Exception as e:
        logger.error(f"❌ Failed to download {filename}: {e}")
        return None

def get_model_paths(quality: str = "int8") -> tuple:
    """Get paths to model and voices files"""
    try:
        # Determine model file based on quality
        if quality == "fp16":
            model_file = "kokoro-npu-fp16.onnx"
            download_model_file = "kokoro-npu-quantized-fp16.onnx"
        else:
            model_file = "kokoro-npu-quantized-int8.onnx"
            download_model_file = "kokoro-npu-quantized-int8.onnx"
        
        voices_file = "voices-v1.0.bin"
        
        # Check for local NPU models first
        local_model_path = os.path.join(LOCAL_NPU_MODEL_DIR, model_file)
        local_voices_path = os.path.join(FALLBACK_MODEL_DIR, voices_file)
        
        if os.path.exists(local_model_path) and os.path.exists(local_voices_path):
            logger.info(f"✅ Using local NPU models: {quality} quality")
            logger.info(f"   Model: {local_model_path}")
            logger.info(f"   Voices: {local_voices_path}")
            return local_model_path, local_voices_path
        
        # Fallback to downloading models
        logger.info("Local NPU models not found, downloading from HuggingFace...")
        model_path = download_model_file(download_model_file)
        voices_path = download_model_file(voices_file)
        
        if model_path and voices_path:
            logger.info(f"✅ Model paths ready: {quality} quality")
            return model_path, voices_path
        else:
            logger.error("❌ Failed to download required model files")
            return None, None
            
    except Exception as e:
        logger.error(f"❌ Error getting model paths: {e}")
        return None, None

class SimpleTTS:
    """Simple TTS class for Unicorn Aware with HuggingFace integration"""
    
    def __init__(self, model_path: Optional[str] = None, voices_path: Optional[str] = None, quality: str = "int8", use_npu: bool = True):
        """Initialize Simple TTS with HuggingFace models"""
        self.model_path = model_path
        self.voices_path = voices_path
        self.quality = quality
        self.use_npu = use_npu
        self.kokoro = None
        self.kokoro_npu = None
        self.unicorn_tts = None
        self.available = False
        self.engine_type = "fallback"
        
        # Try NPU-accelerated TTS using your optimized kokoro-onnx package
        if use_npu and KOKORO_AVAILABLE:
            try:
                logger.info("🚀 Initializing NPU-accelerated Kokoro TTS...")
                # Get model paths (will use local NPU models if available)
                if not model_path or not voices_path:
                    model_path, voices_path = get_model_paths(quality)
                
                if model_path and voices_path:
                    # Use the base model path - the kokoro-onnx package will automatically
                    # detect and use the quantized NPU model if available
                    base_model_path = os.path.join(os.path.dirname(model_path), "../kokoro-v1.0.onnx")
                    if not os.path.exists(base_model_path):
                        # Use the quantized model directly
                        base_model_path = model_path
                    
                    self.kokoro = Kokoro(base_model_path, voices_path)
                    self.available = True
                    self.engine_type = "kokoro_npu"
                    logger.info("✅ NPU-accelerated Kokoro TTS initialized")
                    
                    # Check if NPU acceleration is actually enabled
                    if hasattr(self.kokoro, 'use_npu') and self.kokoro.use_npu:
                        logger.info("✅ NPU acceleration confirmed active")
                    else:
                        logger.info("ℹ️ NPU acceleration attempted, CPU fallback active")
                else:
                    raise Exception("Failed to get model paths")
            except Exception as e:
                logger.warning(f"⚠️ NPU Kokoro TTS failed: {e}")
        
        # Try legacy NPU TTS if available
        if not self.available and use_npu and UNICORN_TTS_AVAILABLE:
            try:
                logger.info("🚀 Initializing legacy NPU-accelerated TTS...")
                self.unicorn_tts = UnicornTTS(model="kokoro-npu-quantized")
                self.available = True
                self.engine_type = "npu"
                logger.info("✅ Legacy NPU-accelerated TTS initialized")
            except Exception as e:
                logger.warning(f"⚠️ Legacy NPU TTS failed: {e}")
        
        # Fallback to standard kokoro-onnx without NPU
        if not self.available and KOKORO_AVAILABLE:
            try:
                logger.info("🚀 Initializing standard Kokoro TTS...")
                # Get model paths
                if not model_path or not voices_path:
                    model_path, voices_path = get_model_paths(quality)
                
                if model_path and voices_path:
                    self.kokoro = Kokoro(model_path, voices_path)
                    self.available = True
                    self.engine_type = "kokoro"
                    logger.info("✅ Standard Kokoro TTS initialized")
                else:
                    raise Exception("Failed to get model paths")
            except Exception as e:
                logger.error(f"❌ Standard TTS initialization failed: {e}")
        
        if not self.available:
            logger.warning("⚠️ All TTS engines failed - using fallback")
            self.kokoro = FallbackKokoro()
            self.engine_type = "fallback"
    
    def synthesize(self, text: str, voice: str = "af_bella") -> bytes:
        """Synthesize text to speech"""
        if not self.available:
            logger.warning("TTS not available")
            return b""
        
        try:
            if (self.engine_type == "kokoro_npu" or self.engine_type == "kokoro") and self.kokoro:
                # Use Kokoro TTS (with or without NPU acceleration)
                audio_array, sample_rate = self.kokoro.create(text, voice)
                logger.info(f"✅ Kokoro-synthesized {len(text)} characters ({self.engine_type})")
                
                # Convert numpy array to bytes for compatibility
                import numpy as np
                if isinstance(audio_array, np.ndarray):
                    # Convert to 16-bit PCM for compatibility
                    audio_int16 = (audio_array * 32767).astype(np.int16)
                    return audio_int16.tobytes()
                else:
                    return b""
            elif self.engine_type == "npu" and self.unicorn_tts:
                # Use legacy NPU-accelerated TTS
                audio = self.unicorn_tts.synthesize(text)
                logger.info(f"✅ Legacy NPU-synthesized {len(text)} characters")
                return audio
            else:
                # Fallback
                logger.warning(f"Using fallback TTS engine: {self.engine_type}")
                return b""
        except Exception as e:
            logger.error(f"❌ TTS synthesis failed: {e}")
            return b""
    
    def save_audio(self, audio: bytes, filename: str):
        """Save audio to file"""
        if not self.available:
            logger.warning("TTS not available")
            return
        
        try:
            # Convert bytes back to numpy array for saving
            import numpy as np
            import soundfile as sf
            
            # Convert bytes to int16 array
            audio_int16 = np.frombuffer(audio, dtype=np.int16)
            # Convert to float32 for saving
            audio_float = audio_int16.astype(np.float32) / 32767.0
            
            # Save using soundfile
            sf.write(filename, audio_float, 24000)  # Kokoro uses 24kHz
            logger.info(f"✅ Audio saved to {filename}")
        except Exception as e:
            logger.error(f"❌ Audio save failed: {e}")
    
    def synthesize_and_save(self, text: str, filename: str, voice: str = "af_bella"):
        """Synthesize text and save to file"""
        audio = self.synthesize(text, voice)
        if audio:
            self.save_audio(audio, filename)
            return True
        return False
    
    def get_available_voices(self) -> list:
        """Get list of available voices"""
        if self.engine_type == "kokoro_npu" and self.kokoro_npu:
            try:
                return self.kokoro_npu.get_voices()
            except Exception as e:
                logger.warning(f"Failed to get voices from NPU engine: {e}")
        
        # Standard Kokoro voices as fallback
        return [
            "af_bella", "af_nicole", "af_sarah", "af_sky",
            "am_adam", "am_michael", "bf_emma", "bf_isabella",
            "bm_george", "bm_lewis"
        ]
    
    def is_available(self) -> bool:
        """Check if TTS is available"""
        return self.available

# Create a default instance with HuggingFace models
default_tts = SimpleTTS(quality="int8")

# Convenience functions
def synthesize_text(text: str, voice: str = "af_bella") -> bytes:
    """Quick text synthesis with HuggingFace models"""
    return default_tts.synthesize(text, voice)

def save_speech(text: str, filename: str, voice: str = "af_bella") -> bool:
    """Quick synthesis and save with HuggingFace models"""
    return default_tts.synthesize_and_save(text, filename, voice)

def is_tts_available() -> bool:
    """Check if TTS is available"""
    return default_tts.is_available()

def get_tts_info() -> dict:
    """Get TTS system information"""
    return {
        "available": default_tts.is_available(),
        "engine_type": default_tts.engine_type,
        "use_npu": default_tts.use_npu,
        "model_path": default_tts.model_path,
        "voices_path": default_tts.voices_path,
        "quality": default_tts.quality,
        "repo": HF_REPO,
        "voices": default_tts.get_available_voices(),
        "kokoro_npu_available": KOKORO_NPU_AVAILABLE,
        "legacy_npu_available": UNICORN_TTS_AVAILABLE,
        "kokoro_available": KOKORO_AVAILABLE
    }

if __name__ == "__main__":
    # Test the TTS system with HuggingFace models
    print("🔊 Testing Simple TTS with HuggingFace Models")
    print(f"🗂️ Using repository: {HF_REPO}")
    
    # Show TTS info
    tts_info = get_tts_info()
    print(f"📊 TTS Status: {'✅ Available' if tts_info['available'] else '❌ Not Available'}")
    print(f"🚀 Engine: {tts_info['engine_type']}")
    print(f"🎛️ Quality: {tts_info['quality']}")
    print(f"🧠 Kokoro NPU Available: {'✅' if tts_info['kokoro_npu_available'] else '❌'}")
    print(f"🔧 Legacy NPU Available: {'✅' if tts_info['legacy_npu_available'] else '❌'}")
    print(f"🔧 Kokoro Available: {'✅' if tts_info['kokoro_available'] else '❌'}")
    print(f"📁 Model: {tts_info['model_path']}")
    print(f"🎤 Voices: {tts_info['voices_path']}")
    
    if is_tts_available():
        print("✅ TTS is available")
        
        # Test synthesis
        test_text = "Hello, this is a test of the Unicorn Aware TTS system using NPU-quantized models from HuggingFace."
        print(f"🎵 Synthesizing: {test_text}")
        audio = synthesize_text(test_text)
        
        if audio:
            print(f"✅ Synthesized {len(audio)} bytes of audio")
            
            # Test save
            if save_speech(test_text, "test_output.wav"):
                print("✅ Audio saved successfully")
            else:
                print("❌ Audio save failed")
        else:
            print("❌ Synthesis failed")
    else:
        print("❌ TTS not available")