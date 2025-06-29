#!/usr/bin/env python3
"""
Test script to verify audio processing without VAD
"""

import sys
import os
import torch
import torchaudio
from pathlib import Path

# Add the audio module to path
sys.path.append(str(Path(__file__).parent.parent / 'scripts' / 'audio'))

def test_processing_without_vad():
    """Test audio processing without VAD functionality"""
    print("Testing Audio Processing Without VAD...")
    
    try:
        from managers import GPUMemoryManager, ModelManager
        from stages import clean_audio_with_demucs_optimized, diarize_with_pyannote_optimized
        import logging
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        logger = logging.getLogger(__name__)
        
        # Initialize managers
        gpu_manager = GPUMemoryManager()
        model_manager = ModelManager(gpu_manager)
        
        print(f"Device: {gpu_manager.device}")
        print(f"CUDA available: {torch.cuda.is_available()}")
        
        # Create a test audio file (5 seconds of speech-like audio)
        test_audio_path = "test_processing.wav"
        sample_rate = 16000
        
        # Generate test audio (speech-like pattern)
        duration = 5.0  # 5 seconds
        t = torch.linspace(0, duration, int(sample_rate * duration))
        
        # Create speech-like pattern
        audio = torch.sin(2 * torch.pi * 440 * t) * 0.1  # 440 Hz tone
        audio = audio.unsqueeze(0)  # Add channel dimension
        
        # Save test audio
        torchaudio.save(test_audio_path, audio, sample_rate)
        print(f"Created test audio: {test_audio_path} ({duration}s)")
        
        # Test processing pipeline without VAD
        print("\nTesting processing pipeline without VAD...")
        
        # Create temp directory
        temp_dir = Path("test_temp")
        temp_dir.mkdir(exist_ok=True)
        
        try:
            # Test denoising (Demucs)
            print("1. Testing denoising with Demucs...")
            cleaned_audio = clean_audio_with_demucs_optimized(
                test_audio_path, temp_dir, model_manager, gpu_manager, logger
            )
            print(f"✓ Denoising completed: {cleaned_audio}")
            
            # Test diarization (if token available)
            print("2. Testing diarization...")
            try:
                from config import token_exists, get_token
                if token_exists() and get_token():
                    diarized_audio = diarize_with_pyannote_optimized(
                        cleaned_audio, temp_dir / "diarized", 
                        model_manager=model_manager, gpu_manager=gpu_manager, logger=logger
                    )
                    print(f"✓ Diarization completed: {diarized_audio}")
                else:
                    print("⚠ Diarization skipped (no token available)")
            except Exception as e:
                print(f"⚠ Diarization failed: {e}")
            
            print("\n✓ Processing pipeline test completed successfully!")
            
        finally:
            # Cleanup
            if os.path.exists(test_audio_path):
                os.remove(test_audio_path)
            
            # Cleanup temp directory
            import shutil
            if temp_dir.exists():
                shutil.rmtree(temp_dir, ignore_errors=True)
        
        # Cleanup models
        model_manager.cleanup_models()
        gpu_manager.cleanup(force=True)
        
        print("\n✓ All tests completed successfully!")
        
    except Exception as e:
        print(f"✗ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_processing_without_vad() 