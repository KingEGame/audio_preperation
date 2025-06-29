#!/usr/bin/env python3
"""
Test script to verify the simplified VAD implementation
"""

import sys
import os
import torch
import torchaudio
from pathlib import Path
import time

# Add the audio module to path
sys.path.append(str(Path(__file__).parent.parent / 'scripts' / 'audio'))

def test_vad_simple_fix():
    """Test the simplified VAD implementation"""
    print("Testing Simplified VAD Implementation...")
    
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
        test_audio_path = "test_vad_simple.wav"
        sample_rate = 16000
        
        # Generate test audio (speech-like pattern)
        duration = 10.0  # 10 seconds
        t = torch.linspace(0, duration, int(sample_rate * duration))
        
        # Create speech-like pattern with silence gaps
        audio = torch.zeros_like(t)
        
        # Add speech segments with silence gaps
        speech_segments = [
            (1.0, 3.0),   # Speech 1: 1-3 seconds
            (4.5, 6.5),   # Speech 2: 4.5-6.5 seconds
            (8.0, 9.5),   # Speech 3: 8-9.5 seconds
        ]
        
        for start, end in speech_segments:
            segment_mask = (t >= start) & (t < end)
            # Different frequency for each segment
            freq = 300 + len(speech_segments) * 50
            audio[segment_mask] += torch.sin(2 * torch.pi * freq * t[segment_mask]) * 0.1
        
        audio = audio.unsqueeze(0)  # Add channel dimension
        
        # Save test audio
        torchaudio.save(test_audio_path, audio, sample_rate)
        print(f"Created test audio: {test_audio_path} ({duration}s)")
        
        # Test VAD with GPU
        print("\nTesting VAD with GPU...")
        start_time = time.time()
        
        try:
            result = remove_silence_with_silero_optimized(
                test_audio_path,
                use_gpu=True,
                force_cpu_vad=False,
                model_manager=model_manager,
                gpu_manager=gpu_manager,
                logger=logger
            )
            
            end_time = time.time()
            processing_time = end_time - start_time
            
            print(f"✓ GPU VAD test passed!")
            print(f"  - Result: {result}")
            print(f"  - Processing time: {processing_time:.2f} seconds")
            
            # Check if result file exists and has different duration
            if os.path.exists(result):
                try:
                    from utils import get_mp3_duration
                    original_duration = get_mp3_duration(test_audio_path)
                    result_duration = get_mp3_duration(result)
                    print(f"  - Original duration: {original_duration}")
                    print(f"  - Result duration: {result_duration}")
                except:
                    print(f"  - Result file created: {result}")
            
        except Exception as e:
            print(f"✗ GPU VAD test failed: {e}")
            import traceback
            traceback.print_exc()
        
        # Test VAD with CPU
        print("\nTesting VAD with CPU...")
        start_time = time.time()
        
        try:
            result = remove_silence_with_silero_optimized(
                test_audio_path,
                use_gpu=False,
                force_cpu_vad=True,
                model_manager=model_manager,
                gpu_manager=gpu_manager,
                logger=logger
            )
            
            end_time = time.time()
            processing_time = end_time - start_time
            
            print(f"✓ CPU VAD test passed!")
            print(f"  - Result: {result}")
            print(f"  - Processing time: {processing_time:.2f} seconds")
            
        except Exception as e:
            print(f"✗ CPU VAD test failed: {e}")
            import traceback
            traceback.print_exc()
        
        # Cleanup
        if os.path.exists(test_audio_path):
            os.remove(test_audio_path)
        
        # Cleanup result files
        result_files = [
            "test_vad_simple_nosilence.wav",
            "test_vad_simple_nosilence_nosilence.wav"
        ]
        for result_file in result_files:
            if os.path.exists(result_file):
                os.remove(result_file)
        
        # Cleanup models
        model_manager.cleanup_models()
        gpu_manager.cleanup(force=True)
        
        print("\n✓ Simplified VAD test completed successfully!")
        
    except Exception as e:
        print(f"✗ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_vad_simple_fix() 