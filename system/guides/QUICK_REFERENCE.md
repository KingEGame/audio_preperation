# Quick Reference - Simplified Audio Processing

## Two Modes Only

### 🚀 Multi-threaded (Fast) - **RECOMMENDED**
```bash
python system\scripts\audio_processing.py --input audio.mp3 --output results
```
- **Best for**: Production, multiple files, high-performance systems
- **Speed**: Fast with GPU acceleration
- **Memory**: 16GB+ recommended

### 🛡️ Single-threaded (Stable)
```bash
python system\scripts\audio_processing.py --input audio.mp3 --output results --mode single
```
- **Best for**: Troubleshooting, compatibility, limited resources
- **Speed**: Slower but more reliable
- **Memory**: 8GB minimum

## Quick Start

### 1. Basic Usage
```bash
python system\scripts\audio_processing.py --input audio.mp3 --output results
```

### 2. Interactive Mode
```bash
python system\scripts\audio_processing.py --interactive
```

### 3. Batch Interface (Easiest)
```bash
system\fixes\simplify_processor.bat
```

### 4. Verbose Logging
```bash
python system\scripts\audio_processing.py --input audio.mp3 --output results --verbose
```

## All Arguments

| Argument | Description | Default |
|----------|-------------|---------|
| `--input`, `-i` | Input file/folder | Required |
| `--output`, `-o` | Output folder | Required |
| `--mode` | `single` or `multithreaded` | `multithreaded` |
| `--verbose`, `-v` | Verbose logging | `False` |
| `--interactive` | Interactive prompts | `False` |

## Processing Stages (Both Modes)

1. **Split** → Divide into 10-minute chunks
2. **Denoise** → Remove background noise
3. **VAD** → Remove silence
4. **Diar** → Separate speakers

## Troubleshooting

### If Multi-threaded Fails
```bash
python system\scripts\audio_processing.py --input audio.mp3 --output results --mode single
```

### Test the Interface
```bash
system\fixes\test_simplified_interface.bat
```

### Check GPU
```bash
system\instructions\test_gpu.bat
```

## Examples

### Single File
```bash
python system\scripts\audio_processing.py --input lecture.mp3 --output results
```

### Multiple Files
```bash
python system\scripts\audio_processing.py --input audio_folder --output results
```

### Stable Mode
```bash
python system\scripts\audio_processing.py --input audio.mp3 --output results --mode single
```

### Interactive
```bash
python system\scripts\audio_processing.py --interactive
```

## Output Structure

```
results/
├── speaker_0/
│   ├── chunk_001.wav
│   ├── chunk_002.wav
│   └── metadata_chunk_001.txt
├── speaker_1/
│   ├── chunk_001.wav
│   └── metadata_chunk_001.txt
└── processing_log.txt
```

## Performance Tips

- **Multi-threaded**: Use for multiple files or high-performance systems
- **Single-threaded**: Use for troubleshooting or limited resources
- **GPU**: Automatically detected and used when available
- **Memory**: Close other applications for best performance

## Need Help?

1. **Test the interface**: `system\fixes\test_simplified_interface.bat`
2. **Check GPU**: `system\instructions\test_gpu.bat`
3. **Full documentation**: `system\guides\SIMPLIFIED_INTERFACE.md`
4. **Troubleshooting**: `system\guides\10-TROUBLESHOOTING.md` 