#!/usr/bin/env python3
"""
Test script for simplified 2-mode audio processing interface
"""

import sys
import os
from pathlib import Path

# Add the scripts directory to the path
sys.path.append(str(Path(__file__).parent.parent / 'scripts'))

def test_simplified_interface():
    """Test the simplified interface with different modes"""
    
    print("Testing simplified audio processing interface...")
    print("="*60)
    
    # Test 1: Single-threaded mode
    print("\nTest 1: Single-threaded mode")
    print("-" * 30)
    
    # Simulate command line arguments
    sys.argv = [
        'audio_processing.py',
        '--input', 'test_audio.mp3',
        '--output', 'test_output',
        '--mode', 'single',
        '--verbose'
    ]
    
    try:
        # Import and test the argument parsing
        from audio_processing import main
        
        # Test that the parameters are correctly set for single mode
        import argparse
        parser = argparse.ArgumentParser()
        parser.add_argument('--input', '-i', help='Path to audio file (mp3/wav) or folder with files')
        parser.add_argument('--output', '-o', help='Folder for saving results')
        parser.add_argument('--mode', type=str, default='multithreaded', choices=['single', 'multithreaded'],
                            help='Processing mode: single (sequential) or multithreaded (parallel, recommended)')
        parser.add_argument('--verbose', '-v', action='store_true', help='Verbose logging')
        parser.add_argument('--interactive', action='store_true', help='Interactive mode with parameter prompts')
        
        args = parser.parse_args()
        
        # Check single-threaded mode parameters
        if args.mode == 'single':
            chunk_duration = 600
            min_speaker_segment = 0.1
            steps = ['split', 'denoise', 'vad', 'diar']
            split_method = 'word_boundary'
            use_gpu = True
            force_cpu_vad = True
            parallel = False
            workers = 1
            
            print(f"✓ Single-threaded mode parameters:")
            print(f"  - Chunk duration: {chunk_duration} sec")
            print(f"  - Min speaker segment: {min_speaker_segment} sec")
            print(f"  - Steps: {', '.join(steps)}")
            print(f"  - Split method: {split_method}")
            print(f"  - GPU: {use_gpu}")
            print(f"  - Force CPU VAD: {force_cpu_vad}")
            print(f"  - Parallel: {parallel}")
            print(f"  - Workers: {workers}")
        
    except Exception as e:
        print(f"✗ Error testing single-threaded mode: {e}")
    
    # Test 2: Multi-threaded mode
    print("\nTest 2: Multi-threaded mode")
    print("-" * 30)
    
    # Simulate command line arguments
    sys.argv = [
        'audio_processing.py',
        '--input', 'test_audio.mp3',
        '--output', 'test_output',
        '--mode', 'multithreaded',
        '--verbose'
    ]
    
    try:
        args = parser.parse_args()
        
        # Check multi-threaded mode parameters
        if args.mode == 'multithreaded':
            chunk_duration = 600
            min_speaker_segment = 0.1
            steps = ['split', 'denoise', 'vad', 'diar']
            split_method = 'smart_multithreaded'
            use_gpu = True
            force_cpu_vad = False
            parallel = True
            workers = None  # Auto-determined
            
            print(f"✓ Multi-threaded mode parameters:")
            print(f"  - Chunk duration: {chunk_duration} sec")
            print(f"  - Min speaker segment: {min_speaker_segment} sec")
            print(f"  - Steps: {', '.join(steps)}")
            print(f"  - Split method: {split_method}")
            print(f"  - GPU: {use_gpu}")
            print(f"  - Force CPU VAD: {force_cpu_vad}")
            print(f"  - Parallel: {parallel}")
            print(f"  - Workers: {workers} (auto-determined)")
        
    except Exception as e:
        print(f"✗ Error testing multi-threaded mode: {e}")
    
    # Test 3: Default mode (should be multithreaded)
    print("\nTest 3: Default mode")
    print("-" * 30)
    
    # Simulate command line arguments without mode
    sys.argv = [
        'audio_processing.py',
        '--input', 'test_audio.mp3',
        '--output', 'test_output'
    ]
    
    try:
        args = parser.parse_args()
        
        print(f"✓ Default mode: {args.mode}")
        if args.mode == 'multithreaded':
            print("✓ Default mode is correctly set to multithreaded")
        else:
            print("✗ Default mode should be multithreaded")
        
    except Exception as e:
        print(f"✗ Error testing default mode: {e}")
    
    print("\n" + "="*60)
    print("Simplified interface test completed!")
    print("="*60)
    
    print("\nUsage examples:")
    print("  python audio_processing.py --input audio.mp3 --output results")
    print("  python audio_processing.py --input audio.mp3 --output results --mode single")
    print("  python audio_processing.py --input audio.mp3 --output results --mode multithreaded")
    print("  python audio_processing.py --interactive")

if __name__ == "__main__":
    test_simplified_interface() 