# Audio Processing Pipeline - Dependencies Guide

## Overview
This guide explains all dependencies required for the audio processing pipeline and provides installation options for different use cases.

## Dependency Categories

### 1. Core Dependencies (Required)
These are essential for basic functionality:

#### PyTorch Ecosystem
- **torch>=2.0.0** - Deep learning framework
- **torchaudio>=2.0.0** - Audio processing for PyTorch
- **numpy>=1.25.2** - Numerical computing
- **scipy>=1.11.4** - Scientific computing

#### Audio Processing
- **librosa>=0.10.1** - Audio analysis library
- **soundfile>=0.12.1** - Audio file I/O
- **ffmpeg-python>=0.2.0** - FFmpeg wrapper
- **pydub>=0.25.1** - Audio manipulation
- **audioread>=3.0.0** - Audio file reading

#### System Monitoring
- **psutil>=5.9.0** - System and process monitoring
- **tqdm>=4.66.1** - Progress bars
- **requests>=2.31.0** - HTTP library
- **urllib3>=1.26.0** - HTTP client

### 2. Advanced Features (Optional)
These enable advanced processing capabilities:

#### Speech Recognition
- **openai-whisper>=20231117** - Speech recognition and transcription
- **transformers>=4.30.0** - HuggingFace transformers library

#### Audio Enhancement
- **demucs>=4.0.1** - Audio source separation (noise removal)

#### Voice Activity Detection
- **silero-vad>=5.1.2** - Voice activity detection

#### Speaker Diarization
- **pyannote.audio>=3.0.0,<4.0.0** - Speaker diarization
- **sentencepiece>=0.1.97,<0.2.0** - Text tokenization
- **speechbrain>=1.0.0,<2.0.0** - Speech processing toolkit

#### HuggingFace Integration
- **huggingface_hub[cli]>=0.19.0** - HuggingFace model hub

## Installation Options

### 1. Full Installation (Recommended)
Includes all features with latest versions:
```bash
system\instructions\install_dependencies_choice.bat
# Choose option 1
```

**Features included:**
- Complete audio processing pipeline
- Speech recognition with Whisper
- Noise removal with Demucs
- Speaker diarization with PyAnnote
- Advanced GPU memory management
- All optimization features

### 2. Alternative Installation
Conservative versions for better compatibility:
```bash
system\instructions\install_dependencies_choice.bat
# Choose option 2
```

**Use when:**
- You have compatibility issues with latest versions
- Your system has older Python/CUDA versions
- You experience installation errors with full version

### 3. Minimal Installation
Basic functionality only:
```bash
system\instructions\install_dependencies_choice.bat
# Choose option 3
```

**Features included:**
- Basic audio processing
- Voice activity detection
- Core utilities
- GPU memory management

**Features NOT included:**
- Speech recognition (Whisper)
- Noise removal (Demucs)
- Speaker diarization (PyAnnote)

### 4. Custom Installation
Choose specific features:
```bash
system\instructions\install_dependencies_choice.bat
# Choose option 4
```

**Options:**
1. Install Whisper only
2. Install Demucs only
3. Install PyAnnote only
4. Install all optional features

## Manual Installation

### Using pip directly:
```bash
# Activate environment first
call audio_environment\Scripts\activate.bat

# Install from specific requirements file
pip install -r system\requirements\requirements.txt
```

### Installing individual packages:
```bash
# Core dependencies
pip install torch torchaudio numpy scipy

# Audio processing
pip install librosa soundfile ffmpeg-python pydub audioread

# System monitoring
pip install psutil tqdm requests urllib3

# Optional: Advanced features
pip install openai-whisper demucs silero-vad
pip install pyannote.audio sentencepiece speechbrain
pip install huggingface_hub[cli] transformers
```

## Version Compatibility

### PyTorch Versions
- **CUDA 12.1**: `torch>=2.0.0` (recommended)
- **CUDA 11.8**: `torch>=1.13.0,<2.1.0` (alternative)
- **CPU only**: `torch>=2.0.0` (no CUDA)

### Python Versions
- **Python 3.8-3.11**: Full support
- **Python 3.12**: Limited support (use alternative versions)

### Operating Systems
- **Windows 10/11**: Full support
- **Linux**: Limited testing
- **macOS**: Limited testing

## Troubleshooting

### Common Installation Issues

#### PyTorch Installation Fails
```bash
# Try alternative CUDA version
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu118

# Or CPU-only version
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cpu
```

#### Demucs Installation Issues
```bash
# Install with specific version
pip install demucs==4.0.1

# Or try alternative version
pip install demucs==3.0.0
```

#### PyAnnote Installation Issues
```bash
# Install with specific constraints
pip install pyannote.audio==3.0.0
pip install sentencepiece==0.1.97
pip install speechbrain==1.0.0
```

#### Memory Issues During Installation
```bash
# Use smaller batch size
pip install --no-cache-dir -r requirements.txt

# Or install packages one by one
pip install torch
pip install torchaudio
# ... continue with other packages
```

### Dependency Conflicts

#### Version Conflicts
```bash
# Check for conflicts
pip check

# Resolve conflicts
pip install --upgrade pip
pip install --force-reinstall package_name
```

#### CUDA Version Mismatch
```bash
# Check CUDA version
nvidia-smi

# Install matching PyTorch version
# For CUDA 11.8:
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu118
# For CUDA 12.1:
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu121
```

## Performance Considerations

### GPU Memory Requirements
- **Demucs**: 2-4 GB GPU memory
- **Whisper**: 1-2 GB GPU memory
- **PyAnnote**: 2-3 GB GPU memory
- **Total**: 6-10 GB GPU memory recommended

### System Memory Requirements
- **Minimal installation**: 4 GB RAM
- **Full installation**: 8 GB RAM (16 GB recommended)
- **Large file processing**: 16+ GB RAM

### Storage Requirements
- **Models**: 2-5 GB disk space
- **Temporary files**: 2-10 GB during processing
- **Output files**: Varies by input size

## Updating Dependencies

### Check for Updates
```bash
pip list --outdated
```

### Update Specific Package
```bash
pip install --upgrade package_name
```

### Update All Dependencies
```bash
pip install --upgrade -r requirements.txt
```

### Reinstall Environment
```bash
# Delete and recreate environment
rmdir /s audio_environment
conda create -n audio_environment python=3.10
conda activate audio_environment
pip install -r system\requirements\requirements.txt
```

## Development Dependencies

### Optional Development Tools
```bash
# Testing
pip install pytest>=7.4.0

# Interactive development
pip install ipython>=8.0.0

# Code formatting
pip install black>=23.0.0

# Linting
pip install flake8>=6.0.0
```

## Security Considerations

### Package Verification
```bash
# Verify package integrity
pip install --require-hashes -r requirements.txt
```

### Virtual Environment
Always use virtual environment to isolate dependencies:
```bash
# Create environment
conda create -n audio_environment python=3.10

# Activate environment
conda activate audio_environment

# Install dependencies
pip install -r requirements.txt
```

## Conclusion

Choose the installation option that best fits your needs:
- **Full installation**: For complete functionality
- **Alternative installation**: For compatibility issues
- **Minimal installation**: For basic features only
- **Custom installation**: For specific requirements

Always verify installation with the provided verification scripts and check the troubleshooting section if you encounter issues. 