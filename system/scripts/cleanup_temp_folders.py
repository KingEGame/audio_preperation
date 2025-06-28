#!/usr/bin/env python3
"""
Cleanup Temporary Processing Folders
Removes old temporary folders created during audio processing
"""

import os
import sys
import shutil
import time
from pathlib import Path
import argparse
import logging

def setup_logging():
    """Setup logging"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    return logging.getLogger(__name__)

def cleanup_temp_folders(project_root, max_age_hours=24, dry_run=False, logger=None):
    """
    Clean up temporary processing folders
    
    Args:
        project_root: Path to project root directory
        max_age_hours: Maximum age of folders to keep (in hours)
        dry_run: If True, only show what would be deleted
        logger: Logger instance
    """
    if logger is None:
        logger = logging.getLogger(__name__)
    
    project_root = Path(project_root)
    if not project_root.exists():
        logger.error(f"Project root does not exist: {project_root}")
        return
    
    logger.info(f"Scanning for temporary folders in: {project_root}")
    
    # Find temporary folders
    temp_patterns = [
        "temp_processing_*",
        "temp_safe_processing_*",
        "tmp*",
        "temp*"
    ]
    
    temp_folders = []
    for pattern in temp_patterns:
        temp_folders.extend(project_root.glob(pattern))
    
    # Filter out non-directories and check age
    current_time = time.time()
    max_age_seconds = max_age_hours * 3600
    
    old_folders = []
    for folder in temp_folders:
        if folder.is_dir():
            try:
                # Get folder creation time (use modification time as fallback)
                stat = folder.stat()
                folder_time = stat.st_ctime if hasattr(stat, 'st_ctime') else stat.st_mtime
                age_seconds = current_time - folder_time
                
                if age_seconds > max_age_seconds:
                    old_folders.append((folder, age_seconds))
                    
            except Exception as e:
                logger.warning(f"Could not check age of {folder}: {e}")
    
    if not old_folders:
        logger.info("No old temporary folders found")
        return
    
    logger.info(f"Found {len(old_folders)} old temporary folders:")
    
    total_size = 0
    for folder, age_seconds in old_folders:
        try:
            # Calculate folder size
            folder_size = sum(f.stat().st_size for f in folder.rglob('*') if f.is_file())
            total_size += folder_size
            
            age_hours = age_seconds / 3600
            size_mb = folder_size / (1024 * 1024)
            
            logger.info(f"  {folder.name}: {age_hours:.1f}h old, {size_mb:.1f} MB")
            
            if not dry_run:
                shutil.rmtree(folder)
                logger.info(f"  ✓ Deleted: {folder.name}")
            else:
                logger.info(f"  [DRY RUN] Would delete: {folder.name}")
                
        except Exception as e:
            logger.error(f"Error processing {folder}: {e}")
    
    total_size_mb = total_size / (1024 * 1024)
    if dry_run:
        logger.info(f"\n[DRY RUN] Would free up {total_size_mb:.1f} MB")
    else:
        logger.info(f"\nFreed up {total_size_mb:.1f} MB")

def main():
    parser = argparse.ArgumentParser(description="Clean up temporary processing folders")
    parser.add_argument('--project-root', help='Project root directory (auto-detected if not specified)')
    parser.add_argument('--max-age', type=int, default=24, help='Maximum age of folders to keep (hours, default 24)')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be deleted without actually deleting')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose logging')
    args = parser.parse_args()
    
    # Setup logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logger = setup_logging()
    
    # Determine project root
    if args.project_root:
        project_root = Path(args.project_root)
    else:
        # Auto-detect project root (3 levels up from this script)
        project_root = Path(__file__).parent.parent.parent
    
    logger.info("=== Temporary Folder Cleanup ===")
    logger.info(f"Project root: {project_root}")
    logger.info(f"Max age: {args.max_age} hours")
    logger.info(f"Dry run: {args.dry_run}")
    
    if args.dry_run:
        print("\n" + "="*60)
        print("DRY RUN MODE - No files will be deleted")
        print("="*60)
    
    cleanup_temp_folders(project_root, args.max_age, args.dry_run, logger)
    
    if not args.dry_run:
        print(f"\nCleanup completed successfully!")
        print(f"Check the log for details.")

if __name__ == "__main__":
    main() 