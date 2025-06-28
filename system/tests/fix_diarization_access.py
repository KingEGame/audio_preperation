#!/usr/bin/env python3
"""
Script for fixing PyAnnote model access issues
"""

import os
import sys
import webbrowser
import time
from pathlib import Path

def open_model_pages():
    """Opens model pages in browser for accepting terms"""
    models = [
        "https://huggingface.co/pyannote/speaker-diarization-3.1",
        "https://huggingface.co/pyannote/segmentation-3.0", 
        "https://huggingface.co/pyannote/embedding-3.0"
    ]
    
    print("Opening model pages in browser...")
    print("For each model:")
    print("1. Click 'Accept' to accept terms of use")
    print("2. Wait for confirmation")
    print("3. Move to next model")
    print()
    
    for i, model_url in enumerate(models, 1):
        print(f"{i}. Opening: {model_url}")
        webbrowser.open(model_url)
        if i < len(models):
            input("Press Enter after accepting terms for this model...")
    
    print("\nAll pages opened. Accept terms for all models.")

def update_token():
    """Updates HuggingFace token"""
    print("\n" + "="*60)
    print("UPDATING HUGGINGFACE TOKEN")
    print("="*60)
    print()
    print("If you have a new token or need to update existing one:")
    print()
    print("1. Go to https://huggingface.co/settings/tokens")
    print("2. Create new token with 'Read' permissions")
    print("3. Copy the token")
    print()
    
    new_token = input("Enter new token (or press Enter to skip): ").strip()
    
    if new_token:
        # Save new token
        token_file = Path(__file__).parent.parent.parent / "hf_token.txt"
        with open(token_file, "w") as f:
            f.write(new_token)
        
        print(f"✓ New token saved to {token_file}")
        return True
    else:
        print("Token not changed.")
        return False

def test_after_fix():
    """Tests access after fixing"""
    print("\n" + "="*60)
    print("TESTING AFTER FIX")
    print("="*60)
    print()
    print("Wait 2-3 minutes after accepting terms, then:")
    print("1. Run: test_diarization_token.bat")
    print("2. Or run audio processing again")
    print()

def main():
    print("FIXING PYANNOTE ACCESS")
    print("="*50)
    print()
    print("This program will help fix PyAnnote model access issues.")
    print()
    
    # Check token availability
    token_file = Path(__file__).parent.parent.parent / "hf_token.txt"
    if not token_file.exists():
        print("✗ hf_token.txt file not found")
        print("First run setup_diarization.py to create token")
        return
    
    with open(token_file, "r") as f:
        token = f.read().strip()
    
    if not token:
        print("✗ Token empty in hf_token.txt file")
        print("First run setup_diarization.py to create token")
        return
    
    print(f"✓ Token found: {token[:10]}...")
    print()
    
    # Show menu
    print("Choose action:")
    print("1. Open model pages to accept terms")
    print("2. Update HuggingFace token")
    print("3. Show fix instructions")
    print("4. Exit")
    print()
    
    choice = input("Enter number (1-4): ").strip()
    
    if choice == "1":
        open_model_pages()
    elif choice == "2":
        update_token()
    elif choice == "3":
        show_instructions()
    elif choice == "4":
        print("Exit.")
        return
    else:
        print("Invalid choice.")
        return
    
    test_after_fix()

def show_instructions():
    """Shows detailed instructions"""
    print("\n" + "="*60)
    print("DETAILED FIX INSTRUCTIONS")
    print("="*60)
    print()
    print("PROBLEM: 'Could not download model' or 'private or gated'")
    print()
    print("SOLUTION:")
    print()
    print("1. ACCEPTING TERMS OF USE:")
    print("   - Go to https://huggingface.co/pyannote/speaker-diarization-3.1")
    print("   - Click 'Accept' button to accept terms")
    print("   - Repeat for other models:")
    print("     * https://huggingface.co/pyannote/segmentation-3.0")
    print("     * https://huggingface.co/pyannote/embedding-3.0")
    print()
    print("2. CHECKING TOKEN:")
    print("   - Go to https://huggingface.co/settings/tokens")
    print("   - Make sure token has 'Read' permissions")
    print("   - Create new token if needed")
    print()
    print("3. TESTING:")
    print("   - Run: test_diarization_token.bat")
    print("   - Or run audio processing again")
    print()
    print("4. WAIT TIME:")
    print("   - After accepting terms wait 2-3 minutes")
    print("   - Changes may not apply instantly")
    print()

if __name__ == "__main__":
    main() 