#!/usr/bin/env python3
"""
Configuration for audio processing pipeline
"""

from pathlib import Path

# Project root folder
PROJECT_ROOT = Path(__file__).parent.parent.parent

# Configuration files
HF_TOKEN_FILE = PROJECT_ROOT / "hf_token.txt"
ACCESS_FILE = PROJECT_ROOT / "Access.txt"  # If needed in future

# Project folders
SYSTEM_DIR = PROJECT_ROOT / "system"
SCRIPTS_DIR = SYSTEM_DIR / "scripts"
INSTRUCTIONS_DIR = SYSTEM_DIR / "instructions"
REQUIREMENTS_DIR = SYSTEM_DIR / "requirements"
GUIDES_DIR = SYSTEM_DIR / "guides"

# Results folders
RESULTS_DIR = PROJECT_ROOT / "results"
TEMP_DIR = PROJECT_ROOT / "temp"

def ensure_directories():
    """Creates necessary folders if they don't exist"""
    directories = [RESULTS_DIR, TEMP_DIR]
    for directory in directories:
        directory.mkdir(exist_ok=True)

def get_token():
    """Gets HuggingFace token from file"""
    if HF_TOKEN_FILE.exists():
        with open(HF_TOKEN_FILE, "r") as f:
            return f.read().strip()
    return None

def save_token(token):
    """Saves HuggingFace token to file"""
    with open(HF_TOKEN_FILE, "w") as f:
        f.write(token)

def token_exists():
    """Checks token existence"""
    return HF_TOKEN_FILE.exists() and get_token() is not None 