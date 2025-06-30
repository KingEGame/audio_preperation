# AllTalk - Dependency Conflict Resolution Guide for CUDA 12.9

## Overview

This guide provides comprehensive solutions for resolving dependency conflicts when setting up AllTalk with CUDA 12.9 support, specifically for modern GPUs like RTX 5080. The guide addresses common issues that arise from version incompatibilities between transformers, faster-whisper, PyTorch, and other components.

## Common Issues and Root Causes

### 1. Transformers Version Conflicts
**Problem**: XTTS streaming requires transformers 4.42.4, but other tools install newer versions (4.43.x+)
**Impact**: Streaming audio generation fails with `TypeError: isin() received an invalid combination of arguments`

### 2. CUDA Architecture Compatibility
**Problem**: PyTorch wheels don't include kernels for new GPU architectures (SM 8.9 for RTX 5080)
**Impact**: `CUDA error: no kernel image is available for execution on the device`

### 3. PyTorch 2.6+ Security Changes
**Problem**: New `weights_only=True` default blocks pickle object loading
**Impact**: `UnpicklingError: Weights only load failed` when loading XTTS checkpoints

### 4. cuDNN DLL Missing
**Problem**: PyTorch 2.x doesn't include cuDNN DLLs in Windows wheels
**Impact**: `Could not locate cudnn_ops_infer64_8.dll`

### 5. Gradio and spaCy Conflicts
**Problem**: Version conflicts between typer, click, and other dependencies
**Impact**: Various import and validation errors

## Step-by-Step Solution

### Step 1: Install Compatible Transformers and faster-whisper Versions

**Why this step is necessary**: XTTS streaming functionality depends on specific transformers API that changed in version 4.43.x. We need to ensure compatibility between transformers, tokenizers, and faster-whisper.

```bash
# Install transformers 4.42.4 (required for XTTS streaming)
pip install transformers==4.42.4

# Install compatible tokenizers version for faster-whisper
pip install tokenizers==0.14

# Install faster-whisper 1.1 (compatible with tokenizers 0.14)
pip install faster-whisper==1.1

# Reinstall transformers to ensure all dependencies are correct
pip install transformers==4.42.4
```

**Expected output**: You may see dependency conflict warnings, but these are expected and can be ignored.

### Step 2: Install PyTorch for CUDA 12.9 (RTX 5080 Support)

**Why this step is necessary**: Standard PyTorch wheels don't include CUDA kernels for SM 8.9 architecture (RTX 5080). We need the nightly build that includes support for newer GPU architectures.

```bash
# Remove existing PyTorch installation
pip uninstall torch torchvision torchaudio -y

# Install nightly PyTorch build for CUDA 12.9
pip install --pre torch torchvision torchaudio --index-url https://download.pytorch.org/whl/nightly/cu129
```

**Verification**: After installation, run:
```bash
python -c "import torch; print(f'PyTorch: {torch.__version__}, CUDA: {torch.version.cuda}'); print(f'GPU: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else \"Not available\"}')"
```

### Step 3: Fix PyTorch 2.6+ weights_only Issue

**Why this step is necessary**: PyTorch 2.6+ introduced security changes that block loading of pickle objects by default. XTTS checkpoints contain configuration objects that need to be explicitly allowed.

Create `sitecustomize.py` in your virtual environment's site-packages directory:
```python
# Location: D:\StoneSegmentation\alltalk2\alltalk_environment\env\Lib\site-packages\sitecustomize.py

import os, importlib.util, pathlib
spec = importlib.util.find_spec("nvidia")
if spec:
    cudnn_dir = pathlib.Path(spec.origin).with_name("cudnn") / "lib"
    if cudnn_dir.exists():
        os.add_dll_directory(str(cudnn_dir))
        os.add_dll_directory("D:\StoneSegmentation\alltalk2\alltalk_environment\env\Lib\site-packages\nvidia\cudnn\bin")

import torch
from torch.serialization import add_safe_globals
from TTS.tts.configs.xtts_config import XttsConfig
from TTS.tts.models.xtts import XttsAudioConfig, XttsArgs
from TTS.config.shared_configs import BaseDatasetConfig

add_safe_globals([XttsConfig, XttsAudioConfig, BaseDatasetConfig, XttsArgs])
```

**How it works**: This file is automatically executed when Python starts, adding the necessary classes to PyTorch's safe globals list and registering the cuDNN DLL directory.

### Step 4: Install cuDNN 8.9 for CUDA 12.9

**Why this step is necessary**: PyTorch 2.x Windows wheels don't include cuDNN DLLs. We need cuDNN 8.9 specifically for compatibility with PyTorch 2.9.

```bash
# Remove cuDNN 9.x if installed
pip uninstall -y nvidia-cudnn-cu12 nvidia-cublas-cu12 nvidia-cuda-nvrtc-cu12

# Install cuDNN 8.9 for CUDA 12
pip install --force-reinstall --no-cache-dir "nvidia-cudnn-cu12==8.9.*"
```

**Verification**: After installation, run:
```bash
python -c "import torch; print(f'cuDNN version: {torch.backends.cudnn.version()}')"
```

**Expected result**: cuDNN version should be 8905 (not 91002)

### Step 5: Resolve Gradio and spaCy Conflicts

**Why this step is necessary**: Gradio 5.x requires typer>=0.12, while spaCy 3.7.x requires typer<0.10. This creates an unsolvable conflict in the same environment.

#### Option A: Compatible Versions (Recommended)

```bash
# Remove conflicting versions
pip uninstall -y gradio gradio-client typer click spacy weasel

# Install compatible package set
pip install "click>=8.1.7" "typer>=0.12" "gradio==5.35.0"

# Reinstall spaCy without dependencies
pip install --no-deps "spacy==3.7.4" "weasel==0.3.4"
```

#### Option B: Downgrade to Gradio 3.50.2 (for finetune.py compatibility)

```bash
# Remove newer versions
pip uninstall -y gradio gradio-client typer click

# Install compatible versions
pip install "gradio==3.50.2" "click>=8.1.7" "typer>=0.12"

# Downgrade Pydantic for compatibility
pip uninstall -y pydantic pydantic-core
pip install "pydantic<2.0" "pydantic-core<2.0"
```

**Why Option B**: finetune.py uses Gradio 3.x API that's incompatible with Gradio 5.x.

### Step 6: Create Working Batch File

**Why this step is necessary**: Proper environment activation and path setup ensures all components work correctly.

Edit `start_finetune.bat`:
```batch
@echo off 
cd /D "D:\StoneSegmentation\alltalk2\" 
set CONDA_ROOT_PREFIX=D:\StoneSegmentation\alltalk2\alltalk_environment\conda 
set INSTALL_ENV_DIR=D:\StoneSegmentation\alltalk2\alltalk_environment\env 
call "D:\StoneSegmentation\alltalk2\alltalk_environment\conda\condabin\conda.bat" activate "D:\StoneSegmentation\alltalk2\alltalk_environment\env" 
set "PATH=%CONDA_PREFIX%\Lib\site-packages\nvidia\cudnn\bin;%PATH%"
call python finetune.py 
```

## Common Error Solutions

### ❌ CUDA error: no kernel image is available for execution on the device

**Cause**: PyTorch doesn't contain kernels for your GPU architecture (SM 8.9 for RTX 5080)

**Solution**:
```bash
# Install nightly PyTorch with CUDA 12.9 support
pip install --pre torch torchvision torchaudio --index-url https://download.pytorch.org/whl/nightly/cu129
```

### ❌ Could not locate cudnn_ops_infer64_8.dll

**Cause**: Missing cuDNN DLL files or wrong version installed

**Solution**:
```bash
# Remove cuDNN 9.x and install cuDNN 8.9
pip uninstall -y nvidia-cudnn-cu12
pip install --force-reinstall --no-cache-dir "nvidia-cudnn-cu12==8.9.*"
```

### ❌ UnpicklingError: Weights only load failed

**Cause**: PyTorch 2.6+ blocks pickle object loading by default

**Solution**: Create `sitecustomize.py` with allow-list (see Step 3)

### ❌ ValidationError: length Input should be a valid integer

**Cause**: Pydantic 2.x vs Gradio 3.50.2 conflict

**Solution**:
```bash
pip uninstall -y pydantic pydantic-core
pip install "pydantic<2.0" "pydantic-core<2.0"
```

### ❌ TypeError: event_trigger() got an unexpected keyword argument 'every'

**Cause**: Gradio 5.x doesn't support `every` argument in `demo.load()`

**Solution**: Downgrade to Gradio 3.50.2 (see Step 5, Option B)

### ❌ cuDNN version: 91002 (instead of 8905)

**Cause**: Installed cuDNN 9.x instead of 8.x

**Solution**: Remove cuDNN 9.x and install cuDNN 8.9.x

## Installation Verification

Run this comprehensive check to verify all components are working:

```bash
python - <<'PY'
import click, typer, gradio, spacy, flask, torch
print("=== Package Versions ===")
print(f"click   : {click.__version__}")
print(f"typer   : {typer.__version__}")
print(f"gradio  : {gradio.__version__}")
print(f"flask   : {flask.__version__}")
print(f"spacy   : {spacy.__version__}")
print(f"torch   : {torch.__version__}")

print("\n=== GPU Information ===")
if torch.cuda.is_available():
    print(f"GPU     : {torch.cuda.get_device_name(0)}")
    print(f"CUDA    : {torch.version.cuda}")
    print(f"cuDNN   : {torch.backends.cudnn.version()}")
    print(f"SM      : {torch.cuda.get_device_capability(0)}")
else:
    print("CUDA not available")

print("\n=== XTTS Compatibility ===")
try:
    from TTS.tts.configs.xtts_config import XttsConfig
    print("✓ XttsConfig import successful")
except ImportError as e:
    print(f"✗ XttsConfig import failed: {e}")

print("\n=== AllTalk Ready ===")

```

## Recommended Package Versions

| Package | Version | Purpose |
|---------|---------|---------|
| transformers | 4.42.4 | Stable version for XTTS streaming |
| tokenizers | 0.19.1 | Compatible with transformers 4.42.4 |
| faster-whisper | 1.1.0 | Compatible with tokenizers 0.19.1 |
| gradio | 3.50.2 | For finetune.py compatibility |
| pydantic | <2.0 | For Gradio 3.50.2 compatibility |
| typer | >=0.12 | For Gradio 3.50.2 |
| click | >=8.1.7 | For Flask 3.0 |
| torch | nightly+cu129 | For CUDA 12.9 and SM 8.9 support |
| nvidia-cudnn-cu12 | 8.9.* | cuDNN 8.x for PyTorch 2.9 Windows |

## Alternative Solutions

### CPU-Only Mode (if GPU is not critical)

```bash
# Temporarily disable GPU
set CUDA_VISIBLE_DEVICES=
python finetune.py
```

### Separate Environment Setup

```bash
# Create separate environment for AllTalk
python -m venv alltalk_env
alltalk_env\Scripts\activate
# Install only necessary packages
```

## Troubleshooting Tips

1. **Check GPU Architecture**: Ensure your GPU is supported by the installed PyTorch version
2. **Verify cuDNN Installation**: Check that cuDNN DLLs are in the correct location
3. **Environment Isolation**: Use separate virtual environments for complex projects
4. **Backup Configuration**: Save working configurations before updates
5. **Import Order**: In sitecustomize.py, cuDNN must be added BEFORE importing torch

## Expected Results

After following all steps, you should see:
- AllTalk starts without errors
- XTTS loads successfully in CUDA
- finetune.py works without ValidationError
- Whisper processes audio without cuDNN errors
- cuDNN version displays correctly (8905, not 91002)

## Next Steps

If you encounter new errors after following this guide, please provide the complete error traceback. Most issues can be resolved by following the dependency logic step-by-step.

## Technical Notes

- **CUDA 12.9**: Latest CUDA version with support for RTX 5080
- **SM 8.9**: Compute capability for RTX 5080 (Ada Lovelace architecture)
- **weights_only**: PyTorch security feature that blocks arbitrary code execution
- **sitecustomize.py**: Python mechanism for automatic code execution at startup
- **cuDNN 8.9**: NVIDIA library for deep learning primitives (compatible with PyTorch 2.9) 