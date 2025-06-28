#!/usr/bin/env python3
"""
Test script for checking GPU and PyTorch availability
"""

import torch
import sys

def test_gpu():
    print("=" * 50)
    print("GPU AND PYTORCH TEST")
    print("=" * 50)
    
    # Check PyTorch version
    print(f"PyTorch version: {torch.__version__}")
    
    # Check CUDA availability
    cuda_available = torch.cuda.is_available()
    print(f"CUDA available: {cuda_available}")
    
    if cuda_available:
        # GPU info
        gpu_count = torch.cuda.device_count()
        print(f"Number of GPUs: {gpu_count}")
        
        for i in range(gpu_count):
            gpu_name = torch.cuda.get_device_name(i)
            gpu_memory = torch.cuda.get_device_properties(i).total_memory / 1024**3
            print(f"GPU {i}: {gpu_name} ({gpu_memory:.1f} GB)")
        
        # Current GPU
        current_device = torch.cuda.current_device()
        print(f"Current GPU: {current_device}")
        
        # Performance test
        print("\nGPU performance test...")
        try:
            # Create test tensor on GPU
            x = torch.randn(1000, 1000).cuda()
            y = torch.randn(1000, 1000).cuda()
            
            # Measure matrix multiplication time
            import time
            start_time = time.time()
            for _ in range(100):
                z = torch.mm(x, y)
            torch.cuda.synchronize()  # Wait for GPU operations to finish
            end_time = time.time()
            
            print(f"Time for 100 matrix multiplications 1000x1000: {end_time - start_time:.3f} sec")
            print("GPU test passed successfully!")
            
        except Exception as e:
            print(f"Error during GPU test: {e}")
            return False
    else:
        print("CUDA not available. Please check:")
        print("1. Are NVIDIA drivers installed?")
        print("2. Is PyTorch installed with CUDA support?")
        print("3. Is the CUDA version compatible?")
        return False
    
    # Check other libraries
    print("\nChecking other libraries...")
    
    try:
        import torchaudio
        print(f"✓ torchaudio: {torchaudio.__version__}")
    except ImportError:
        print("✗ torchaudio is not installed")
    
    try:
        import whisper
        print(f"✓ whisper: {whisper.__version__}")
    except ImportError:
        print("✗ whisper is not installed")
    
    try:
        from demucs.pretrained import get_model
        print("✓ demucs is available")
    except ImportError:
        print("✗ demucs is not installed")
    
    try:
        from silero import vad
        print("✓ silero-vad is available")
    except ImportError:
        print("✗ silero-vad is not installed")
    
    print("\n" + "=" * 50)
    if cuda_available:
        print("✅ GPU IS READY!")
        print("Audio processing will use GPU acceleration.")
    else:
        print("⚠️  GPU NOT AVAILABLE")
        print("Audio processing will run on CPU (slower).")
    print("=" * 50)
    
    return cuda_available

if __name__ == "__main__":
    test_gpu() 