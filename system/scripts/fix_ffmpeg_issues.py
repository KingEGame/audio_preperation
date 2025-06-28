#!/usr/bin/env python3
"""
FFmpeg Issue Diagnostics and Fixes
Helps identify and resolve common FFmpeg errors like 4294967268
"""

import os
import sys
import subprocess
import logging
from pathlib import Path
import shutil

def setup_logging():
    """Setup logging for diagnostics"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    return logging.getLogger(__name__)

def check_ffmpeg_installation():
    """Check if FFmpeg is properly installed"""
    logger = logging.getLogger(__name__)
    
    print("="*60)
    print("FFMPEG INSTALLATION CHECK")
    print("="*60)
    
    # Check if ffmpeg is in PATH
    ffmpeg_path = shutil.which("ffmpeg")
    if ffmpeg_path:
        print(f"✓ FFmpeg found in PATH: {ffmpeg_path}")
    else:
        print("✗ FFmpeg not found in PATH")
        return False
    
    # Check if ffprobe is available
    ffprobe_path = shutil.which("ffprobe")
    if ffprobe_path:
        print(f"✓ FFprobe found in PATH: {ffprobe_path}")
    else:
        print("✗ FFprobe not found in PATH")
        return False
    
    # Test FFmpeg version
    try:
        result = subprocess.run(["ffmpeg", "-version"], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            version_line = result.stdout.split('\n')[0]
            print(f"✓ FFmpeg version: {version_line}")
        else:
            print("✗ FFmpeg version check failed")
            return False
    except Exception as e:
        print(f"✗ Error checking FFmpeg version: {e}")
        return False
    
    return True

def test_audio_file_processing(audio_file):
    """Test processing of a specific audio file"""
    logger = logging.getLogger(__name__)
    
    print("\n" + "="*60)
    print("AUDIO FILE PROCESSING TEST")
    print("="*60)
    
    if not Path(audio_file).exists():
        print(f"✗ Audio file not found: {audio_file}")
        return False
    
    file_size = Path(audio_file).stat().st_size
    print(f"✓ File exists, size: {file_size} bytes")
    
    if file_size == 0:
        print("✗ File is empty")
        return False
    
    # Test basic FFmpeg info
    try:
        result = subprocess.run([
            "ffprobe", "-v", "quiet", "-print_format", "json",
            "-show_format", "-show_streams", audio_file
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("✓ FFprobe can read file successfully")
        else:
            print(f"✗ FFprobe failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"✗ FFprobe error: {e}")
        return False
    
    # Test basic conversion
    output_file = Path(audio_file).parent / "test_output.wav"
    try:
        command = [
            "ffmpeg", "-i", audio_file,
            "-vn", "-acodec", "pcm_s16le", "-ar", "16000", "-ac", "1",
            "-y", str(output_file)
        ]
        
        result = subprocess.run(command, capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            print("✓ Basic conversion successful")
            if output_file.exists():
                output_file.unlink()  # Clean up
        else:
            print(f"✗ Basic conversion failed: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print("✗ Basic conversion timeout")
        return False
    except Exception as e:
        print(f"✗ Basic conversion error: {e}")
        return False
    
    return True

def check_system_resources():
    """Check system resources that might affect FFmpeg"""
    logger = logging.getLogger(__name__)
    
    print("\n" + "="*60)
    print("SYSTEM RESOURCES CHECK")
    print("="*60)
    
    try:
        import psutil
        
        # Check disk space
        disk_usage = psutil.disk_usage('.')
        free_gb = disk_usage.free / (1024**3)
        print(f"✓ Free disk space: {free_gb:.1f} GB")
        
        if free_gb < 1.0:
            print("⚠ Low disk space - may cause FFmpeg errors")
        
        # Check memory
        memory = psutil.virtual_memory()
        available_gb = memory.available / (1024**3)
        print(f"✓ Available memory: {available_gb:.1f} GB")
        
        if available_gb < 2.0:
            print("⚠ Low memory - may cause FFmpeg errors")
        
        # Check CPU
        cpu_count = psutil.cpu_count()
        print(f"✓ CPU cores: {cpu_count}")
        
    except ImportError:
        print("⚠ psutil not available - skipping resource check")
    except Exception as e:
        print(f"⚠ Error checking resources: {e}")

def suggest_fixes():
    """Suggest fixes for common FFmpeg issues"""
    print("\n" + "="*60)
    print("SUGGESTED FIXES")
    print("="*60)
    
    print("1. If FFmpeg is not found:")
    print("   - Run: system\\instructions\\download_ffmpeg.bat")
    print("   - Or download from: https://ffmpeg.org/download.html")
    
    print("\n2. If audio files are corrupted:")
    print("   - Try different audio files")
    print("   - Check file format compatibility")
    print("   - Verify file integrity")
    
    print("\n3. If system resources are low:")
    print("   - Free up disk space")
    print("   - Close other applications")
    print("   - Restart the system")
    
    print("\n4. If FFmpeg crashes with error 4294967268:")
    print("   - Try processing smaller audio chunks")
    print("   - Use different audio codec settings")
    print("   - Check for corrupted audio files")
    print("   - Update FFmpeg to latest version")
    
    print("\n5. Alternative processing options:")
    print("   - Skip problematic stages (denoise, vad, diar)")
    print("   - Use simple splitting instead of word boundary")
    print("   - Process files one by one instead of parallel")

def main():
    """Main diagnostic function"""
    logger = setup_logging()
    
    print("FFMPEG DIAGNOSTICS AND FIXES")
    print("="*60)
    
    # Check FFmpeg installation
    ffmpeg_ok = check_ffmpeg_installation()
    
    # Check system resources
    check_system_resources()
    
    # Test specific file if provided
    if len(sys.argv) > 1:
        audio_file = sys.argv[1]
        print(f"\nTesting specific file: {audio_file}")
        file_ok = test_audio_file_processing(audio_file)
    else:
        print("\nNo specific file provided for testing")
        print("To test a specific file, run: python fix_ffmpeg_issues.py <audio_file>")
        file_ok = None
    
    # Provide suggestions
    suggest_fixes()
    
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    
    if ffmpeg_ok:
        print("✓ FFmpeg installation appears to be working")
    else:
        print("✗ FFmpeg installation has issues")
    
    if file_ok is True:
        print("✓ Audio file processing test passed")
    elif file_ok is False:
        print("✗ Audio file processing test failed")
    else:
        print("? Audio file processing test not performed")
    
    print("\nIf you continue to have issues:")
    print("1. Check the log file: audio_processing.log")
    print("2. Try processing with fewer stages")
    print("3. Use smaller audio chunks")
    print("4. Contact support with error details")

if __name__ == "__main__":
    main() 