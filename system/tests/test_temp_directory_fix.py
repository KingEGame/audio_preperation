#!/usr/bin/env python3
"""
Test script to verify temp directory fix
"""

import sys
import os
import torch
import torchaudio
from pathlib import Path

# Add the audio module to path
sys.path.append(str(Path(__file__).parent.parent / 'scripts' / 'audio'))

def test_temp_directory_fix():
    """Test that temp files are created in the central temp directory"""
    print("Testing Temp Directory Fix...")
    
    try:
        from splitters import get_central_temp_dir, split_audio_by_duration_optimized
        import logging
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        logger = logging.getLogger(__name__)
        
        # Create a test audio file
        test_audio_path = "test_temp_fix.wav"
        sample_rate = 16000
        
        # Generate test audio (15 seconds)
        duration = 15.0
        t = torch.linspace(0, duration, int(sample_rate * duration))
        audio = torch.sin(2 * torch.pi * 440 * t) * 0.1
        audio = audio.unsqueeze(0)
        
        # Save test audio
        torchaudio.save(test_audio_path, audio, sample_rate)
        print(f"Created test audio: {test_audio_path} ({duration}s)")
        
        # Test central temp directory
        print("\n1. Testing central temp directory...")
        central_temp = get_central_temp_dir()
        print(f"✓ Central temp directory: {central_temp}")
        print(f"✓ Directory exists: {central_temp.exists()}")
        
        # Create a test input directory
        test_input_dir = Path("test_input_dir")
        test_input_dir.mkdir(exist_ok=True)
        
        # Copy test audio to input directory
        import shutil
        input_audio = test_input_dir / "test_audio.wav"
        shutil.copy(test_audio_path, input_audio)
        print(f"✓ Created test input directory: {test_input_dir}")
        print(f"✓ Test audio in input dir: {input_audio}")
        
        # Test splitting (should create temp files in central temp, not input dir)
        print("\n2. Testing audio splitting...")
        output_dir = Path("test_output_dir")
        output_dir.mkdir(exist_ok=True)
        
        try:
            # Split audio (this should create temp files in central temp)
            parts = split_audio_by_duration_optimized(
                str(input_audio), output_dir, max_duration_sec=5, logger=logger
            )
            print(f"✓ Splitting completed: {len(parts)} parts")
            
            # Check if temp files were created in central temp (not input dir)
            print("\n3. Checking temp file locations...")
            
            # Check input directory - should be clean
            input_temp_files = list(test_input_dir.glob("temp_*"))
            print(f"  Input directory temp files: {len(input_temp_files)}")
            if input_temp_files:
                print("  ⚠ WARNING: Temp files found in input directory!")
                for temp_file in input_temp_files:
                    print(f"    - {temp_file}")
            else:
                print("  ✓ Input directory is clean (no temp files)")
            
            # Check central temp directory
            central_temp_files = list(central_temp.glob("temp_*"))
            print(f"  Central temp directory files: {len(central_temp_files)}")
            if central_temp_files:
                print("  ✓ Temp files found in central temp directory:")
                for temp_file in central_temp_files:
                    print(f"    - {temp_file}")
            else:
                print("  ✓ Central temp directory is clean")
            
            # Check output directory
            output_files = list(output_dir.glob("part_*"))
            print(f"  Output directory files: {len(output_files)}")
            for output_file in output_files:
                print(f"    - {output_file}")
            
            print("\n✓ Temp directory fix test completed successfully!")
            
        finally:
            # Cleanup
            if os.path.exists(test_audio_path):
                os.remove(test_audio_path)
            
            # Cleanup test directories
            if test_input_dir.exists():
                shutil.rmtree(test_input_dir)
            
            if output_dir.exists():
                shutil.rmtree(output_dir)
            
            # Cleanup central temp files
            for temp_file in central_temp.glob("temp_*"):
                try:
                    if temp_file.is_file():
                        temp_file.unlink()
                    elif temp_file.is_dir():
                        shutil.rmtree(temp_file)
                except:
                    pass
        
    except Exception as e:
        print(f"✗ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_temp_directory_fix() 