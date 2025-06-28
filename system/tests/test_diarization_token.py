#!/usr/bin/env python3
"""
Script for testing HuggingFace token and diagnosing PyAnnote issues (via huggingface_hub)
Additionally tests diarization on real audio file
"""

from huggingface_hub import HfApi
from huggingface_hub.utils import HfHubHTTPError
from pathlib import Path
import tempfile
import subprocess
import os
import sys

def test_hf_token(token):
    print(f"Testing token: {token[:10]}...")
    api = HfApi(token=token)
    try:
        user_info = api.whoami()
        print(f"✓ Token valid! User: {user_info.get('name')}")
        return True
    except Exception as e:
        print(f"✗ Token invalid or error: {e}")
        return False

def test_model_access(token, model_name):
    print(f"Testing access to model: {model_name}")
    api = HfApi(token=token)
    try:
        model_info = api.model_info(model_name)
        print(f"✓ Access to model {model_name} allowed")
        print(f"  - Author: {model_info.author}")
        # Check for license attribute before using it
        if hasattr(model_info, 'license'):
            print(f"  - License: {model_info.license}")
        else:
            print(f"  - License: information unavailable")
        return True
    except HfHubHTTPError as e:
        if e.response.status_code == 404:
            print(f"✗ Model {model_name} not found")
        elif e.response.status_code == 401:
            print(f"✗ No access to model {model_name} (401 Unauthorized)")
        elif e.response.status_code == 403:
            print(f"✗ Access to model {model_name} forbidden (403 Forbidden)")
            print("  Possible reasons:")
            print("  1. Model terms of use not accepted")
            print("  2. Token doesn't have access rights")
            print("  3. Model is private")
        else:
            print(f"✗ Model access error: {e}")
        return False
    except Exception as e:
        print(f"✗ Model testing error: {e}")
        return False

def create_test_audio():
    """
    Creates simple test audio file using ffmpeg
    """
    print("Creating test audio file...")
    
    # Create file in current directory
    test_audio = Path("temp.mp3")
    
    try:
        # Create simple audio file with 440Hz tone for 60 seconds
        command = [
            "ffmpeg", "-f", "lavfi", "-i", "sine=frequency=440:duration=60",
            "-ar", "16000", "-ac", "1", str(test_audio),
            "-y"  # Overwrite if exists
        ]
        
        result = subprocess.run(command, capture_output=True, text=True)
        
        if result.returncode == 0 and test_audio.exists():
            print(f"✓ Test audio file created: {test_audio}")
            return test_audio
        else:
            print(f"✗ Error creating test audio: {result.stderr}")
            return None
            
    except Exception as e:
        print(f"✗ Error creating test audio: {e}")
        return None

def test_diarization_with_audio(token, audio_file):
    """
    Tests diarization on real audio file
    """
    print(f"\nTesting diarization on file: {audio_file}")
    
    
    try:
        from pyannote.audio import Pipeline
        from pyannote.audio.pipelines.utils.hook import ProgressHook
        import torch
    except ImportError as e:
        print(f"✗ PyAnnote not installed: {e}")
        print("Run setup_diarization.py for installation")
        return False
    
    # Check GPU availability
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")
    
    try:
        # Load diarization model
        print("Loading diarization model...")
        pipeline = Pipeline.from_pretrained(
            "pyannote/speaker-diarization-3.1",
            use_auth_token=token
        )
        
        # Move model to GPU if available
        if device.type == "cuda":
            pipeline = pipeline.to(device)
            print("Model moved to GPU")
        
        # Perform diarization
        print("Executing diarization...")
        with ProgressHook() as hook:
            diarization = pipeline(audio_file, hook=hook)
        
        # Analyze results
        speakers = set()
        total_duration = 0
        
        for turn, _, speaker in diarization.itertracks(yield_label=True):
            speakers.add(speaker)
            total_duration += turn.end - turn.start
        
        print(f"✓ Diarization completed successfully!")
        print(f"  - Speakers detected: {len(speakers)}")
        print(f"  - Speakers: {', '.join(sorted(speakers))}")
        print(f"  - Total speech duration: {total_duration:.2f} sec")
        
        # Create simple report
        output_dir = Path("test_diarization_results")
        output_dir.mkdir(exist_ok=True)
        
        rttm_file = output_dir / "test_diarization.rttm"
        with open(rttm_file, 'w') as f:
            diarization.write_rttm(f)
        
        report_file = output_dir / "test_diarization_report.txt"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("TEST DIARIZATION REPORT\n")
            f.write("="*50 + "\n\n")
            f.write(f"Test file: {audio_file}\n")
            f.write(f"Speakers detected: {len(speakers)}\n")
            f.write(f"Speakers: {', '.join(sorted(speakers))}\n")
            f.write(f"Total speech duration: {total_duration:.2f} sec\n\n")
            f.write("DETAILED REPORT:\n")
            f.write("-"*30 + "\n")
            for turn, _, speaker in diarization.itertracks(yield_label=True):
                start_time = turn.start
                end_time = turn.end
                duration = end_time - start_time
                f.write(f"{speaker}: {start_time:.2f}s - {end_time:.2f}s (duration: {duration:.2f}s)\n")
        
        print(f"  - RTTM file: {rttm_file}")
        print(f"  - Report: {report_file}")
        
        return True
        
    except Exception as e:
        error_msg = str(e)
        print(f"✗ Error during diarization: {error_msg}")
        
        # Check error type and give recommendations
        if "Could not download" in error_msg or "private or gated" in error_msg:
            print("PROBLEM: Model not downloaded due to token or terms of use issues")
            print("SOLUTION:")
            print("1. Run: quick_diarization_setup.bat")
            print("2. Or follow instructions in DIARIZATION_SETUP_GUIDE.md")
            print("3. Make sure you accepted terms of use on HuggingFace")
        elif "NoneType" in error_msg:
            print("PROBLEM: Model not initialized")
            print("SOLUTION: Check token and restart diarization setup")
        else:
            print("PROBLEM: Unexpected error during diarization")
            print("SOLUTION: Check internet connection and try again")
        
        return False

def main():
    print("TOKEN DIAGNOSTICS AND DIARIZATION TESTING")
    print("="*50)
    
    # Read token from file
    token_file = Path(__file__).parent.parent.parent / "hf_token.txt"
    if not token_file.exists():
        print("✗ hf_token.txt file not found")
        print("Run setup_diarization.py to setup token")
        return
    
    with open(token_file, "r") as f:
        token = f.read().strip()
    
    if not token:
        print("✗ Token empty in hf_token.txt file")
        print("Run setup_diarization.py to setup token")
        return
    
    print(f"Found token: {token[:10]}...")
    
    # Test token
    if not test_hf_token(token):
        print("\nSOLUTION:")
        print("1. Go to https://huggingface.co/settings/tokens")
        print("2. Create new token with 'Read' permissions")
        print("3. Run setup_diarization.py and enter new token")
        return
    
    # Test access to PyAnnote models
    models_to_test = [
        "pyannote/speaker-diarization-3.1"
    ]
    
    print("\nTesting access to PyAnnote models:")
    all_models_accessible = True
    
    for model in models_to_test:
        print(f"\n--- {model} ---")
        if not test_model_access(token, model):
            all_models_accessible = False
    
    if not all_models_accessible:
        print("\n" + "="*50)
        print("⚠️  MODEL ACCESS ISSUES")
        print("="*50)
        print("Follow instructions above to fix.")
        return
    
    # Test diarization on real audio file
    print("\n" + "="*50)
    print("TESTING DIARIZATION ON REAL AUDIO")
    print("="*50)
    
    # Use test audio file in current directory
    test_audio = Path("temp.mp3")
    
    if not test_audio.exists():
        print(f"✗ Audio file not found: {test_audio}")
        print("Creating test audio file...")
        test_audio = create_test_audio()
        if not test_audio:
            print("Failed to create test audio file. Check ffmpeg installation.")
            return
    else:
        print(f"✓ Using existing audio file: {test_audio}")
    
    # Test diarization
    diarization_success = test_diarization_with_audio(token, test_audio)
    
    # Clean up temporary files only if this was created test file
    if "temp.mp3" in str(test_audio) and test_audio.exists():
        try:
            test_audio.unlink()
            print(f"Test file deleted: {test_audio}")
        except Exception as e:
            print(f"Failed to delete test file: {e}")
    
    # Final result
    print("\n" + "="*50)
    if diarization_success:
        print("✅ DIARIZATION WORKING CORRECTLY!")
        print("="*50)
        print("All tests passed successfully. Diarization ready to use.")
    else:
        print("❌ DIARIZATION ISSUES")
        print("="*50)
        print("Follow instructions above to fix issues.")

if __name__ == "__main__":
    main() 