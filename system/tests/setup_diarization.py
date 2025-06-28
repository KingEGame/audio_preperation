#!/usr/bin/env python3
"""
PyAnnote diarization setup script
"""

import subprocess
import sys
import os
from pathlib import Path

def install_pyannote():
    """Installs PyAnnote and dependencies with correct versions"""
    print("Installing PyAnnote and dependencies...")
    
    # First fix NumPy to compatible version
    print("Fixing NumPy version...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "numpy>=1.25.2", "--force-reinstall"])
        print("✓ NumPy fixed")
    except subprocess.CalledProcessError as e:
        print(f"✗ Error fixing NumPy: {e}")
        return False
    
    packages = [
        "torch>=1.12.0",
        "torchaudio>=0.12.0", 
        "librosa",
        "soundfile",
        "pyannote.audio"
    ]
    
    for package in packages:
        print(f"Installing {package}...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"✓ {package} installed")
        except subprocess.CalledProcessError as e:
            print(f"✗ Error installing {package}: {e}")
            return False
    
    return True

def get_hf_token():
    """Helps get HuggingFace token"""
    print("\n" + "="*60)
    print("PYANNOTE TOKEN SETUP")
    print("="*60)
    print()
    print("To use PyAnnote diarization, you need a HuggingFace token:")
    print()
    print("1. Go to https://huggingface.co/pyannote/speaker-diarization-3.1")
    print("2. Click 'Accept' to accept terms of use")
    print("3. Go to Settings -> Access Tokens")
    print("4. Create new token with 'Read' permissions")
    print("5. Copy the token")
    print()
    
    token = input("Enter your HuggingFace token: ").strip()
    
    if not token:
        print("Token not entered. Diarization will be skipped.")
        return None
    
    # Save token to file
    token_file = Path(__file__).parent.parent.parent / "hf_token.txt"
    with open(token_file, "w") as f:
        f.write(token)
    
    print(f"✓ Token saved to {token_file}")
    return token

def test_pyannote():
    """Tests PyAnnote installation"""
    print("\nTesting PyAnnote...")
    
    try:
        # Check NumPy
        import numpy
        print(f"✓ NumPy: {numpy.__version__}")
        
        # Check numba
        import numba
        print("✓ numba working")
        
        # Check PyAnnote
        from pyannote.audio import Pipeline
        print("✓ PyAnnote imported successfully")
        
        # Check token
        token_file = Path(__file__).parent.parent.parent / "hf_token.txt"
        if os.path.exists(token_file):
            with open(token_file, "r") as f:
                token = f.read().strip()
            
            if token:
                print("✓ Token found")
                return True
            else:
                print("✗ Token is empty")
                return False
        else:
            print("✗ Token file not found")
            return False
            
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False
    except Exception as e:
        print(f"✗ Testing error: {e}")
        return False

def main():
    print("PYANNOTE DIARIZATION SETUP")
    print("="*40)
    
    # Install PyAnnote
    if not install_pyannote():
        print("Error installing PyAnnote")
        return
    
    # Get token
    token = get_hf_token()
    
    # Test
    if test_pyannote():
        print("\n" + "="*60)
        print("✅ DIARIZATION READY TO USE!")
        print("="*60)
        print()
        print("Now you can use 'diar' stage in audio processing:")
        print("start_audio_processing.bat --input audio.mp3 --output results --steps split denoise vad diar")
    else:
        print("\n" + "="*60)
        print("⚠️  DIARIZATION NOT SETUP")
        print("="*60)
        print()
        print("Check:")
        print("1. PyAnnote installation")
        print("2. HuggingFace token availability")
        print("3. Model terms of use acceptance")
        print()
        print("If there are NumPy issues, run:")
        print("fix_numpy_diarization.bat")

if __name__ == "__main__":
    main() 