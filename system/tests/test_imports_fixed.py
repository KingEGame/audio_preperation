#!/usr/bin/env python3
"""
Test script to verify that all imports are working correctly
"""

import sys
from pathlib import Path

# Add the scripts directory to path
scripts_dir = Path(__file__).parent.parent / 'scripts'
sys.path.append(str(scripts_dir))

def test_imports():
    """Test that all imports work correctly"""
    print("Testing Audio Module Imports...")
    
    try:
        # Test basic imports
        print("1. Testing basic imports...")
        from audio import (
            GPUMemoryManager, ModelManager,
            process_audio_file_optimized, parallel_audio_processing_optimized,
            process_multiple_files_parallel_optimized,
            clean_audio_with_demucs_optimized, 
            diarize_with_pyannote_optimized,
            split_audio_by_duration_optimized, split_audio_at_word_boundary_optimized,
            get_mp3_duration, setup_logging, copy_results_to_output_optimized,
            get_optimal_workers, setup_gpu_optimization, 
            MAX_WORKERS, GPU_MEMORY_LIMIT, BATCH_SIZE
        )
        print("✓ All basic imports successful")
        
        # Test managers
        print("2. Testing managers...")
        gpu_manager = GPUMemoryManager()
        model_manager = ModelManager(gpu_manager)
        print("✓ Managers created successfully")
        
        # Test config functions
        print("3. Testing config functions...")
        workers = get_optimal_workers()
        gpu_available = setup_gpu_optimization()
        print(f"✓ Optimal workers: {workers}")
        print(f"✓ GPU available: {gpu_available}")
        
        # Test logging
        print("4. Testing logging...")
        logger = setup_logging()
        logger.info("Test log message")
        print("✓ Logging setup successful")
        
        # Test constants
        print("5. Testing constants...")
        print(f"✓ MAX_WORKERS: {MAX_WORKERS}")
        print(f"✓ GPU_MEMORY_LIMIT: {GPU_MEMORY_LIMIT}")
        print(f"✓ BATCH_SIZE: {BATCH_SIZE}")
        
        print("\n✓ All imports and basic functionality working correctly!")
        return True
        
    except Exception as e:
        print(f"✗ Import test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_imports()
    if success:
        print("\n🎉 All tests passed! The audio processing system is ready to use.")
    else:
        print("\n❌ Some tests failed. Please check the errors above.") 