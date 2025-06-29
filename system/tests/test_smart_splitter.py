#!/usr/bin/env python3
"""
Test script for the new smart multithreaded splitter
"""

import sys
import os
import torch
import torchaudio
from pathlib import Path
import time

# Add the audio module to path
sys.path.append(str(Path(__file__).parent.parent / 'scripts' / 'audio'))

def test_smart_splitter():
    """Test the new smart multithreaded splitter"""
    print("Testing Smart Multithreaded Splitter...")
    
    try:
        from managers import GPUMemoryManager, ModelManager
        from splitters import split_audio_smart_multithreaded_optimized
        import logging
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        logger = logging.getLogger(__name__)
        
        # Initialize managers
        gpu_manager = GPUMemoryManager()
        model_manager = ModelManager(gpu_manager)
        
        print(f"Device: {gpu_manager.device}")
        print(f"CUDA available: {torch.cuda.is_available()}")
        
        # Create a test audio file (2 minutes of speech-like audio)
        test_audio_path = "test_smart_splitter.wav"
        sample_rate = 16000
        
        # Generate test audio (multiple sine waves to simulate speech)
        duration = 120.0  # 2 minutes
        t = torch.linspace(0, duration, int(sample_rate * duration))
        
        # Create speech-like pattern with multiple frequencies
        audio = torch.zeros_like(t)
        for i in range(10):  # 10 segments
            start_time = i * 12  # 12 seconds per segment
            end_time = start_time + 10  # 10 seconds duration
            segment_mask = (t >= start_time) & (t < end_time)
            
            # Different frequency for each segment
            freq = 200 + i * 50  # 200-650 Hz
            audio[segment_mask] += torch.sin(2 * torch.pi * freq * t[segment_mask]) * 0.05
        
        audio = audio.unsqueeze(0)  # Add channel dimension
        
        # Save test audio
        torchaudio.save(test_audio_path, audio, sample_rate)
        print(f"Created test audio: {test_audio_path} ({duration}s)")
        
        # Test smart splitter with 30-second chunks
        print("\nTesting Smart Multithreaded Splitter...")
        start_time = time.time()
        
        try:
            parts = split_audio_smart_multithreaded_optimized(
                test_audio_path,
                temp_dir="test_smart_splitter_temp",
                max_duration_sec=30,  # 30-second chunks
                whisper_model=model_manager.get_whisper_model("base"),
                max_workers=4,
                logger=logger
            )
            
            end_time = time.time()
            processing_time = end_time - start_time
            
            print(f"✓ Smart splitter test passed!")
            print(f"  - Created {len(parts)} parts")
            print(f"  - Processing time: {processing_time:.2f} seconds")
            print(f"  - Speed: {duration/processing_time:.2f}x real-time")
            
            # Show parts info
            for i, part in enumerate(parts):
                part_path = Path(part)
                if part_path.exists():
                    try:
                        from utils import get_mp3_duration
                        duration_str = get_mp3_duration(str(part_path))
                        print(f"    Part {i+1}: {part_path.name} ({duration_str})")
                    except:
                        print(f"    Part {i+1}: {part_path.name}")
            
        except Exception as e:
            print(f"✗ Smart splitter test failed: {e}")
            import traceback
            traceback.print_exc()
        
        # Cleanup
        if os.path.exists(test_audio_path):
            os.remove(test_audio_path)
        
        # Cleanup temp directory
        temp_dir = Path("test_smart_splitter_temp")
        if temp_dir.exists():
            import shutil
            shutil.rmtree(temp_dir)
        
        # Cleanup models
        model_manager.cleanup_models()
        gpu_manager.cleanup(force=True)
        
        print("\n✓ Smart splitter test completed successfully!")
        
    except Exception as e:
        print(f"✗ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_smart_splitter() 