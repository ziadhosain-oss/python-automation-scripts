#!/usr/bin/env python3
"""
Automated Backup Tool - Create compressed backups of important files
Usage: python3 backup_tool.py [source] [destination]
"""

import os
import shutil
import argparse
from datetime import datetime
from pathlib import Path
import tarfile
import zipfile

def get_size(bytes):
    """Convert bytes to human readable format"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes < 1024.0:
            return f"{bytes:.2f} {unit}"
        bytes /= 1024.0

def create_backup(source_path, dest_path, compression='zip', exclude_patterns=None):
    """
    Create a compressed backup of source directory
    
    Args:
        source_path: Path to backup
        dest_path: Destination for backup file
        compression: Type of compression ('zip' or 'tar.gz')
        exclude_patterns: List of patterns to exclude
    """
    source_path = os.path.expanduser(source_path)
    dest_path = os.path.expanduser(dest_path)
    
    if not os.path.exists(source_path):
        print(f"❌ Error: Source path '{source_path}' does not exist!")
        return False
    
    # Create destination directory if it doesn't exist
    os.makedirs(dest_path, exist_ok=True)
    
    # Generate backup filename with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    source_name = os.path.basename(os.path.normpath(source_path))
    
    if compression == 'zip':
        backup_filename = f"{source_name}_backup_{timestamp}.zip"
    else:
        backup_filename = f"{source_name}_backup_{timestamp}.tar.gz"
    
    backup_path = os.path.join(dest_path, backup_filename)
    
    print(f"\n{'='*70}")
    print(f"💾 CREATING BACKUP")
    print(f"{'='*70}")
    print(f"Source: {source_path}")
    print(f"Destination: {backup_path}")
    print(f"Compression: {compression}")
    print(f"{'='*70}\n")
    
    # Track statistics
    file_count = 0
    total_size = 0
    excluded_count = 0
    
    exclude_patterns = exclude_patterns or []
    
    def should_exclude(path):
        """Check if path matches any exclude pattern"""
        for pattern in exclude_patterns:
            if pattern in path:
                return True
        return False
    
    try:
        if compression == 'zip':
            with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                if os.path.isfile(source_path):
                    zipf.write(source_path, os.path.basename(source_path))
                    file_count = 1
                    total_size = os.path.getsize(source_path)
                    print(f"✅ Added: {os.path.basename(source_path)}")
                else:
                    for root, dirs, files in os.walk(source_path):
                        # Filter out excluded directories
                        dirs[:] = [d for d in dirs if not should_exclude(os.path.join(root, d))]
                        
                        for file in files:
                            filepath = os.path.join(root, file)
                            
                            if should_exclude(filepath):
                                excluded_count += 1
                                continue
                            
                            try:
                                arcname = os.path.relpath(filepath, source_path)
                                zipf.write(filepath, arcname)
                                file_size = os.path.getsize(filepath)
                                total_size += file_size
                                file_count += 1
                                
                                if file_count % 100 == 0:
                                    print(f"  Processed {file_count} files...")
                            except (OSError, PermissionError) as e:
                                print(f"⚠️  Error adding {filepath}: {e}")
        
        else:  # tar.gz
            with tarfile.open(backup_path, 'w:gz') as tar:
                if os.path.isfile(source_path):
                    tar.add(source_path, arcname=os.path.basename(source_path))
                    file_count = 1
                    total_size = os.path.getsize(source_path)
                    print(f"✅ Added: {os.path.basename(source_path)}")
                else:
                    for root, dirs, files in os.walk(source_path):
                        dirs[:] = [d for d in dirs if not should_exclude(os.path.join(root, d))]
                        
                        for file in files:
                            filepath = os.path.join(root, file)
                            
                            if should_exclude(filepath):
                                excluded_count += 1
                                continue
                            
                            try:
                                arcname = os.path.relpath(filepath, source_path)
                                tar.add(filepath, arcname=arcname)
                                file_size = os.path.getsize(filepath)
                                total_size += file_size
                                file_count += 1
                                
                                if file_count % 100 == 0:
                                    print(f"  Processed {file_count} files...")
                            except (OSError, PermissionError) as e:
                                print(f"⚠️  Error adding {filepath}: {e}")
        
        backup_size = os.path.getsize(backup_path)
        compression_ratio = (1 - backup_size / total_size) * 100 if total_size > 0 else 0
        
        print(f"\n{'='*70}")
        print(f"✅ BACKUP COMPLETE")
        print(f"{'='*70}")
        print(f"Files backed up: {file_count}")
        if excluded_count > 0:
            print(f"Files excluded: {excluded_count}")
        print(f"Original size: {get_size(total_size)}")
        print(f"Backup size: {get_size(backup_size)}")
        print(f"Compression: {compression_ratio:.1f}%")
        print(f"Backup saved to: {backup_path}")
        print(f"{'='*70}\n")
        
        return True
    
    except Exception as e:
        print(f"\n❌ Error creating backup: {e}")
        # Clean up partial backup
        if os.path.exists(backup_path):
            os.remove(backup_path)
        return False

def list_backups(backup_dir):
    """List all backups in a directory"""
    backup_dir = os.path.expanduser(backup_dir)
    
    if not os.path.exists(backup_dir):
        print(f"❌ Error: Backup directory '{backup_dir}' does not exist!")
        return
    
    backups = []
    for file in os.listdir(backup_dir):
        if file.endswith(('.zip', '.tar.gz')) and '_backup_' in file:
            filepath = os.path.join(backup_dir, file)
            size = os.path.getsize(filepath)
            mtime = os.path.getmtime(filepath)
            backups.append((file, size, mtime))
    
    if not backups:
        print(f"No backups found in {backup_dir}")
        return
    
    backups.sort(key=lambda x: x[2], reverse=True)
    
    print(f"\n{'='*70}")
    print(f"📦 AVAILABLE BACKUPS in {backup_dir}")
    print(f"{'='*70}\n")
    
    for filename, size, mtime in backups:
        date_str = datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S')
        print(f"📁 {filename}")
        print(f"   Size: {get_size(size)}")
        print(f"   Date: {date_str}")
        print()

def main():
    parser = argparse.ArgumentParser(description='Create automated backups')
    parser.add_argument('source', nargs='?', default='~/Documents',
                        help='Source path to backup (default: ~/Documents)')
    parser.add_argument('destination', nargs='?', default='~/Backups',
                        help='Destination for backup (default: ~/Backups)')
    parser.add_argument('--format', choices=['zip', 'tar.gz'], default='zip',
                        help='Compression format (default: zip)')
    parser.add_argument('--exclude', nargs='+', default=[],
                        help='Patterns to exclude (e.g., __pycache__ .git node_modules)')
    parser.add_argument('--list', action='store_true',
                        help='List existing backups in destination')
    
    args = parser.parse_args()
    
    if args.list:
        list_backups(args.destination)
    else:
        # Add common exclude patterns
        exclude_patterns = args.exclude + ['__pycache__', '.pyc', '.tmp', '~']
        create_backup(args.source, args.destination, args.format, exclude_patterns)

if __name__ == "__main__":
    main()
