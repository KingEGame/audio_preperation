# Simplified Audio Processing Interface

## Overview

The audio processing pipeline now features a simplified 2-mode interface with pre-configured optimal parameters for maximum ease of use.

## Two Processing Modes

### 1. Single-threaded Mode (Stable)
- **Purpose**: Sequential processing for maximum stability and compatibility
- **Best for**: Troubleshooting, compatibility issues, or when GPU resources are limited
- **Speed**: Slower but more reliable

**Pre-configured Parameters:**
- Chunk duration: 600 seconds (10 minutes)
- Minimum speaker segment: 0.1 seconds (no limit)
- Splitting method: `word_boundary` (Whisper-based)
- VAD device: CPU (for compatibility)
- Parallel processing: Disabled
- Workers: 1

### 2. Multi-threaded Mode (Fast) - **RECOMMENDED**
- **Purpose**: Parallel processing for maximum speed and efficiency
- **Best for**: Production use, multiple files, high-performance systems
- **Speed**: Significantly faster with GPU acceleration

**Pre-configured Parameters:**
- Chunk duration: 600 seconds (10 minutes)
- Minimum speaker segment: 0.1 seconds (no limit)
- Splitting method: `smart_multithreaded` (GPU-accelerated)
- VAD device: GPU (with CPU fallback)
- Parallel processing: Enabled
- Workers: Auto-determined based on system

## Usage

### Command Line Interface

```bash
# Basic usage (defaults to multithreaded mode)
python system\scripts\audio_processing.py --input audio.mp3 --output results

# Single-threaded mode
python system\scripts\audio_processing.py --input audio.mp3 --output results --mode single

# Multi-threaded mode (explicit)
python system\scripts\audio_processing.py --input audio.mp3 --output results --mode multithreaded

# Interactive mode
python system\scripts\audio_processing.py --interactive

# Verbose logging
python system\scripts\audio_processing.py --input audio.mp3 --output results --verbose
```

### Simplified Batch Interface

Use the simplified batch script for even easier operation:

```bash
system\fixes\simplify_processor.bat
```

This will prompt you to:
1. Choose mode (1=single, 2=multithreaded)
2. Enter input file/folder
3. Enter output folder

### Interactive Mode

When using `--interactive` or when input/output are not provided:

```
============================================================
AUDIO PROCESSING PIPELINE (SIMPLIFIED)
============================================================

Enter path to audio file or folder with audio files:
Examples:
  - audio.mp3
  - C:\path\to\audio.mp3
  - audio_folder
  - C:\path\to\audio_folder
Input file/folder: audio.mp3

Enter folder for saving results:
Examples:
  - results
  - C:\path\to\results
Output folder: results

Current settings (multithreaded mode):
  - Chunk duration: 600 sec (10 minutes)
  - Minimum speaker segment: 0.1 sec (no limit)
  - Splitting method: smart_multithreaded
  - Processing stages: split, denoise, vad, diar
  - GPU acceleration: Yes
  - VAD device: GPU
  - Parallel processing: Yes
  - Number of processes: 4

Current mode: multithreaded
  single - Sequential processing (stable, slower)
  multithreaded - Parallel processing (fast, recommended)
Change mode? (y/n, default n): n

Starting processing with parameters:
  Input: audio.mp3
  Output: results
  Mode: multithreaded
  Splitting: smart_multithreaded
  GPU: Yes
  Parallel: Yes

Continue? (y/n, default y): y
```

## Available Arguments

| Argument | Description | Default | Choices |
|----------|-------------|---------|---------|
| `--input`, `-i` | Input audio file or folder | Required | Any path |
| `--output`, `-o` | Output folder for results | Required | Any path |
| `--mode` | Processing mode | `multithreaded` | `single`, `multithreaded` |
| `--verbose`, `-v` | Enable verbose logging | `False` | Flag |
| `--interactive` | Interactive mode with prompts | `False` | Flag |

## Processing Stages

Both modes include the same processing stages:
1. **Split**: Divide audio into manageable chunks
2. **Denoise**: Remove background noise using Demucs
3. **VAD**: Remove silence using Silero VAD
4. **Diar**: Speaker diarization using PyAnnote

## Performance Comparison

| Mode | Speed | Stability | GPU Usage | Best For |
|------|-------|-----------|-----------|----------|
| Single-threaded | Slower | High | Limited | Troubleshooting, compatibility |
| Multi-threaded | Fast | Good | Full | Production, multiple files |

## System Requirements

### Single-threaded Mode
- CPU: Any modern processor
- RAM: 8GB minimum
- GPU: Optional (CPU fallback available)

### Multi-threaded Mode
- CPU: Multi-core processor (recommended: 6+ cores)
- RAM: 16GB minimum (32GB recommended)
- GPU: NVIDIA GPU with CUDA support (recommended)

## Troubleshooting

### If Single-threaded Mode Fails
- Check if all dependencies are installed
- Verify audio file format (MP3/WAV)
- Check available disk space
- Review error logs

### If Multi-threaded Mode Fails
- Try single-threaded mode first
- Check GPU drivers and CUDA installation
- Reduce number of parallel processes
- Check available RAM

### Common Issues
1. **Diarization token missing**: Will prompt to set up automatically
2. **GPU out of memory**: Automatically falls back to CPU
3. **File not found**: Check input path and file permissions

## Testing

Test the simplified interface:

```bash
system\fixes\test_simplified_interface.bat
```

This will verify that both modes are working correctly with the pre-configured parameters.

## Migration from Old Interface

If you were using the old complex interface with many arguments:

**Old:**
```bash
python audio_processing.py --input audio.mp3 --output results --chunk_duration 600 --min_speaker_segment 0.1 --split_method smart_multithreaded --use_gpu --parallel --workers 4
```

**New:**
```bash
python audio_processing.py --input audio.mp3 --output results --mode multithreaded
```

All the optimal parameters are now pre-configured based on the selected mode. 