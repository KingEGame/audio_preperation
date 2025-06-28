#!/usr/bin/env python3
"""
Script for concatenating MP3 files using ffmpeg.
Combines files in the order of their names and saves the result.
"""

import os
import sys
import subprocess
import argparse
import logging
from pathlib import Path
from tqdm import tqdm

def setup_logging(log_level=logging.INFO):
    """
    Configures logging with timestamps and formatting.
    :param log_level: Logging level.
    """
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('concatenate_mp3.log', encoding='utf-8')
        ]
    )
    return logging.getLogger(__name__)

def get_mp3_duration(file_path):
    """
    Gets the duration of an MP3 file using ffprobe.
    :param file_path: Path to the MP3 file.
    :return: String with duration in HH:MM:SS format.
    """
    try:
        result = subprocess.run([
            "ffprobe", "-v", "quiet", "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1", file_path
        ], capture_output=True, text=True, check=True)
        
        duration_seconds = float(result.stdout.strip())
        hours = int(duration_seconds // 3600)
        minutes = int((duration_seconds % 3600) // 60)
        seconds = int(duration_seconds % 60)
        
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    except subprocess.CalledProcessError:
        print(f"Error getting duration for file: {file_path}")
        return "00:00:00"

def concatenate_mp3_files(input_dir, output_file, file_pattern="*.mp3", sort_by_name=True, logger=None):
    """
    Concatenates MP3 files from the specified folder into one file.
    
    :param input_dir: Folder with MP3 files
    :param output_file: Path to the output file
    :param file_pattern: Pattern for finding files (default *.mp3)
    :param sort_by_name: Whether to sort files by name
    :param logger: Logger for messages
    :return: True if successful, False otherwise
    """
    if logger is None:
        logger = logging.getLogger(__name__)
    
    input_path = Path(input_dir)
    output_path = Path(output_file)
    
    # Check if input folder exists
    if not input_path.exists():
        logger.error(f"Input folder not found: {input_path}")
        return False
    
    if not input_path.is_dir():
        logger.error(f"Specified path is not a folder: {input_path}")
        return False
    
    # Find all MP3 files
    mp3_files = list(input_path.glob(file_pattern))
    
    if not mp3_files:
        logger.error(f"No MP3 files found in folder: {input_path}")
        return False
    
    # Sort files by name if needed
    if sort_by_name:
        mp3_files.sort(key=lambda x: x.name)
    
    logger.info(f"Found {len(mp3_files)} MP3 files")
    print(f"Found {len(mp3_files)} MP3 files:")
    
    # Show list of files with their durations
    total_duration_seconds = 0
    for i, file_path in enumerate(mp3_files, 1):
        duration_str = get_mp3_duration(str(file_path))
        print(f"  {i:2d}. {file_path.name} ({duration_str})")
        
        # Calculate total duration
        time_parts = duration_str.split(":")
        hours = int(time_parts[0])
        minutes = int(time_parts[1])
        seconds = int(time_parts[2])
        total_duration_seconds += hours * 3600 + minutes * 60 + seconds
    
    # Convert total duration back to HH:MM:SS format
    total_hours = int(total_duration_seconds // 3600)
    total_minutes = int((total_duration_seconds % 3600)) // 60
    total_seconds = int(total_duration_seconds % 60)
    total_duration_str = f"{total_hours:02d}:{total_minutes:02d}:{total_seconds:02d}"
    
    print(f"\nTotal duration: {total_duration_str}")
    logger.info(f"Total duration: {total_duration_str}")
    
    # Create folder for output file if needed
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Create temporary file list for ffmpeg
    temp_list_file = output_path.parent / "temp_file_list.txt"
    
    try:
        with open(temp_list_file, 'w', encoding='utf-8') as f:
            for file_path in mp3_files:
                # Use absolute paths for reliability
                f.write(f"file '{file_path.absolute()}'\n")
        
        logger.info("Temporary file list created")
        
        # Run concatenation via ffmpeg
        print(f"\nStarting concatenation...")
        logger.info(f"Starting concatenation to file: {output_path}")
        
        command = [
            "ffmpeg", "-f", "concat", "-safe", "0",
            "-i", str(temp_list_file),
            "-c", "copy", str(output_path),
            "-y"  # Overwrite if exists
        ]
        
        # Run ffmpeg with progress bar
        with tqdm(total=1, desc="Concatenation", unit="operation") as pbar:
            result = subprocess.run(command, capture_output=True, text=True)
            pbar.update(1)
        
        if result.returncode == 0 and output_path.exists():
            # Check size and duration of created file
            file_size = output_path.stat().st_size / (1024 * 1024)  # in MB
            final_duration = get_mp3_duration(str(output_path))
            
            print(f"\n✅ Concatenation completed successfully!")
            print(f"📁 Output file: {output_path}")
            print(f"📊 Size: {file_size:.2f} MB")
            print(f"⏱️  Duration: {final_duration}")
            
            logger.info(f"Concatenation completed successfully: {output_path}")
            logger.info(f"Size: {file_size:.2f} MB, Duration: {final_duration}")
            
            return True
        else:
            print(f"\n❌ Error during concatenation!")
            print(f"stderr: {result.stderr}")
            logger.error(f"Error during concatenation: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        logger.error(f"Unexpected error during concatenation: {e}")
        return False
    finally:
        # Remove temporary file
        if temp_list_file.exists():
            temp_list_file.unlink()
            logger.info("Temporary file removed")

def main():
    parser = argparse.ArgumentParser(description="Concatenate MP3 files using ffmpeg")
    parser.add_argument('--input', '-i', help='Folder with MP3 files')
    parser.add_argument('--output', '-o', help='Path to output MP3 file')
    parser.add_argument('--pattern', '-p', default='*.mp3', help='Pattern for finding files (default *.mp3)')
    parser.add_argument('--no-sort', action='store_true', help='Do not sort files by name')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose logging')
    parser.add_argument('--interactive', action='store_true', help='Interactive mode')
    args = parser.parse_args()

    # Configure logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logger = setup_logging(log_level)
    
    logger.info("=== Starting MP3 concatenation ===")

    # Interactive mode
    if args.interactive:
        print("\n" + "="*60)
        print("MP3 FILES CONCATENATION")
        print("="*60)
        
        # Get input folder
        if not args.input:
            print("\nEnter the path to the folder with MP3 files:")
            print("Examples:")
            print("  - audio_files")
            print("  - C:\\path\\to\\audio_files")
            args.input = input("Input folder: ").strip().strip('"')
        
        # Get output file
        if not args.output:
            print("\nEnter the path to the output MP3 file:")
            print("Examples:")
            print("  - combined.mp3")
            print("  - C:\\path\\to\\combined.mp3")
            args.output = input("Output file: ").strip().strip('"')
        
        # Additional settings
        print(f"\nCurrent settings:")
        print(f"  - File pattern: {args.pattern}")
        print(f"  - Sort by name: {'No' if args.no_sort else 'Yes'}")
        
        change_settings = input("\nChange settings? (y/n, default n): ").strip().lower()
        if change_settings in ['y', 'yes']:
            # File pattern
            new_pattern = input(f"File pattern (default {args.pattern}): ").strip()
            if new_pattern:
                args.pattern = new_pattern
            
            # Sorting
            sort_choice = input("Sort files by name? (y/n, default y): ").strip().lower()
            args.no_sort = sort_choice in ['n', 'no']
        
        print(f"\nStarting concatenation with parameters:")
        print(f"  Input folder: {args.input}")
        print(f"  Output file: {args.output}")
        print(f"  File pattern: {args.pattern}")
        print(f"  Sort by name: {'No' if args.no_sort else 'Yes'}")
        
        confirm = input("\nContinue? (y/n, default y): ").strip().lower()
        if confirm in ['n', 'no']:
            print("Concatenation cancelled.")
            return
    else:
        # Check required arguments only in non-interactive mode
        if not args.input:
            parser.error("--input/-i is required when not using --interactive")
        if not args.output:
            parser.error("--output/-o is required when not using --interactive")

    logger.info(f"Input parameters: {vars(args)}")

    # Perform concatenation
    success = concatenate_mp3_files(
        input_dir=args.input,
        output_file=args.output,
        file_pattern=args.pattern,
        sort_by_name=not args.no_sort,
        logger=logger
    )
    
    if success:
        logger.info("=== Concatenation completed successfully ===")
        print(f"\n{'='*60}")
        print("CONCATENATION COMPLETED SUCCESSFULLY!")
        print(f"{'='*60}")
        print(f"Result saved to: {args.output}")
        print(f"Log saved to: concatenate_mp3.log")
    else:
        logger.error("=== Concatenation finished with error ===")
        print(f"\n{'='*60}")
        print("CONCATENATION FINISHED WITH ERROR!")
        print(f"{'='*60}")
        print("Check the log file: concatenate_mp3.log")

if __name__ == "__main__":
    main() 