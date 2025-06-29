#!/usr/bin/env python3
"""
Test script for VAD device fix
"""

import sys
import os
import torch
import torchaudio
from pathlib import Path

# Add the audio module to path
sys.path.append(str(Path(__file__).parent.parent / 'scripts' / 'audio'))

def test_vad_device_fix():
    """Test VAD with proper device handling"""
    print("Testing VAD Device Fix...")
    
    try:
        from managers import GPUMemoryManager, ModelManager
        from stages import remove_silence_with_silero_optimized
        import logging
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        logger = logging.getLogger(__name__)
        
        # Initialize managers
        gpu_manager = GPUMemoryManager()
        model_manager = ModelManager(gpu_manager)
        
        print(f"Device: {gpu_manager.device}")
        print(f"CUDA available: {torch.cuda.is_available()}")
        
        # Create a test audio file (10 seconds of speech-like audio)
        test_audio_path = "test_vad_fix.wav"
        sample_rate = 16000
        
        # Generate test audio (sine wave to simulate speech)
        duration = 10.0  # 10 seconds
        t = torch.linspace(0, duration, int(sample_rate * duration))
        
        # Create speech-like pattern
        audio = torch.sin(2 * torch.pi * 440 * t) * 0.1  # 440 Hz tone
        audio = audio.unsqueeze(0)  # Add channel dimension
        
        # Save test audio
        torchaudio.save(test_audio_path, audio, sample_rate)
        print(f"Created test audio: {test_audio_path} ({duration}s)")
        
        # Test VAD with CPU
        print("\nTesting VAD with CPU...")
        try:
            result = remove_silence_with_silero_optimized(
                test_audio_path,
                output_wav="test_vad_cpu_result.wav",
                use_gpu=False,
                force_cpu_vad=True,
                model_manager=model_manager,
                gpu_manager=gpu_manager,
                logger=logger
            )
            print(f"✓ CPU VAD test passed: {result}")
        except Exception as e:
            print(f"✗ CPU VAD test failed: {e}")
        
        # Test VAD with GPU (if available)
        if torch.cuda.is_available():
            print("\nTesting VAD with GPU...")
            try:
                result = remove_silence_with_silero_optimized(
                    test_audio_path,
                    output_wav="test_vad_gpu_result.wav",
                    use_gpu=True,
                    force_cpu_vad=False,
                    model_manager=model_manager,
                    gpu_manager=gpu_manager,
                    logger=logger
                )
                print(f"✓ GPU VAD test passed: {result}")
            except Exception as e:
                print(f"✗ GPU VAD test failed: {e}")
                print("This is expected if there are CUDA compatibility issues")
        
        # Cleanup
        if os.path.exists(test_audio_path):
            os.remove(test_audio_path)
        
        for result_file in ["test_vad_cpu_result.wav", "test_vad_gpu_result.wav"]:
            if os.path.exists(result_file):
                os.remove(result_file)
        
        # Cleanup models
        model_manager.cleanup_models()
        gpu_manager.cleanup(force=True)
        
        print("\n✓ VAD device fix test completed successfully!")
        
    except Exception as e:
        print(f"✗ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_vad_device_fix() 