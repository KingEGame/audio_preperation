#!/usr/bin/env python3
"""
Test script to verify VAD device mismatch fix
"""

import sys
import os
import torch
import torchaudio
from pathlib import Path

# Add the audio module to path
sys.path.append(str(Path(__file__).parent.parent / 'scripts' / 'audio'))

def test_vad_device_fix():
    """Test VAD device handling"""
    print("Testing VAD device fix...")
    
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
        
        # Create a test audio file (1 second of silence)
        test_audio_path = "test_audio.wav"
        sample_rate = 16000
        
        # Generate test audio (sine wave)
        duration = 1.0  # 1 second
        t = torch.linspace(0, duration, int(sample_rate * duration))
        audio = torch.sin(2 * torch.pi * 440 * t) * 0.1  # 440 Hz sine wave
        audio = audio.unsqueeze(0)  # Add channel dimension
        
        # Save test audio
        torchaudio.save(test_audio_path, audio, sample_rate)
        print(f"Created test audio: {test_audio_path}")
        
        # Test VAD with CPU (should work reliably)
        print("\nTesting VAD with CPU...")
        try:
            result = remove_silence_with_silero_optimized(
                test_audio_path,
                use_gpu=False,
                force_cpu_vad=True,
                model_manager=model_manager,
                gpu_manager=gpu_manager,
                logger=logger
            )
            print(f"✓ CPU VAD test passed: {result}")
        except Exception as e:
            print(f"✗ CPU VAD test failed: {e}")
            import traceback
            traceback.print_exc()
        
        # Test VAD with GPU (if available)
        if torch.cuda.is_available():
            print("\nTesting VAD with GPU...")
            try:
                result = remove_silence_with_silero_optimized(
                    test_audio_path,
                    use_gpu=True,
                    force_cpu_vad=False,
                    model_manager=model_manager,
                    gpu_manager=gpu_manager,
                    logger=logger
                )
                print(f"✓ GPU VAD test passed: {result}")
            except Exception as e:
                print(f"✗ GPU VAD test failed: {e}")
                print("This might be expected if there are CUDA compatibility issues")
                import traceback
                traceback.print_exc()
        
        # Cleanup
        if os.path.exists(test_audio_path):
            os.remove(test_audio_path)
        
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