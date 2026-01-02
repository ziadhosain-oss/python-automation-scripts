#!/usr/bin/env python3
"""
Duplicate File Finder - Find and optionally remove duplicate files
Usage: python3 duplicate_finder.py [folder_path] [--delete]
"""

import os
import hashlib
import argparse
from pathlib import Path
from collections import defaultdict

def get_file_hash(filepath, block_size=65536):
    """Calculate MD5 hash of a file"""
    hasher = hashlib.md5()
    try:
        with open(filepath, 'rb') as f:
            while True:
                data = f.read(block_size)
                if not data:
                    break
                hasher.update(data)
        return hasher.hexdigest()
    except (IOError, PermissionError) as e:
        print(f"⚠️  Error reading {filepath}: {e}")
        return None

def get_file_size(filepath):
    """Get file size in bytes"""
    try:
        return os.path.getsize(filepath)
    except OSError:
        return 0

def format_size(bytes):
    """Convert bytes to human readable format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes < 1024.0:
            return f"{bytes:.2f} {unit}"
        bytes /= 1024.0
    return f"{bytes:.2f} TB"

def find_duplicates(folder_path, recursive=True):
    """
    Find duplicate files in a folder
    
    Args:
        folder_path: Path to search for duplicates
        recursive: Whether to search subdirectories
    
    Returns:
        Dictionary mapping file hashes to lists of duplicate file paths
    """
    print(f"\n{'='*70}")
    print(f"🔍 Searching for duplicate files in: {folder_path}")
    print(f"{'='*70}\n")
    
    # First pass: Group files by size (faster than hashing)
    size_groups = defaultdict(list)
    file_count = 0
    
    if recursive:
        for root, dirs, files in os.walk(folder_path):
            for filename in files:
                filepath = os.path.join(root, filename)
                file_size = get_file_size(filepath)
                if file_size > 0:  # Skip empty files
                    size_groups[file_size].append(filepath)
                    file_count += 1
    else:
        for item in os.listdir(folder_path):
            filepath = os.path.join(folder_path, item)
            if os.path.isfile(filepath):
                file_size = get_file_size(filepath)
                if file_size > 0:
                    size_groups[file_size].append(filepath)
                    file_count += 1
    
    print(f"📊 Scanned {file_count} files")
    
    # Second pass: Hash files with matching sizes
    hash_groups = defaultdict(list)
    potential_dupes = sum(1 for files in size_groups.values() if len(files) > 1)
    
    if potential_dupes == 0:
        print("✅ No duplicate files found!")
        return {}
    
    print(f"🔄 Checking {sum(len(files) for files in size_groups.values() if len(files) > 1)} potential duplicates...")
    
    checked = 0
    for file_size, files in size_groups.items():
        if len(files) > 1:  # Only hash files with matching sizes
            for filepath in files:
                file_hash = get_file_hash(filepath)
                if file_hash:
                    hash_groups[file_hash].append(filepath)
                checked += 1
                if checked % 100 == 0:
                    print(f"  Processed {checked} files...")
    
    # Filter to only groups with duplicates
    duplicates = {h: files for h, files in hash_groups.items() if len(files) > 1}
    
    return duplicates

def display_duplicates(duplicates):
    """Display found duplicate files"""
    if not duplicates:
        print("\n✅ No duplicate files found!")
        return 0
    
    total_wasted_space = 0
    duplicate_count = 0
    
    print(f"\n{'='*70}")
    print(f"📋 DUPLICATE FILES FOUND")
    print(f"{'='*70}\n")
    
    for i, (file_hash, files) in enumerate(duplicates.items(), 1):
        file_size = get_file_size(files[0])
        wasted_space = file_size * (len(files) - 1)
        total_wasted_space += wasted_space
        duplicate_count += len(files) - 1
        
        print(f"Duplicate Set #{i}")
        print(f"  File size: {format_size(file_size)}")
        print(f"  Wasted space: {format_size(wasted_space)}")
        print(f"  Copies: {len(files)}")
        print(f"  Hash: {file_hash}")
        print(f"  Files:")
        
        for filepath in files:
            print(f"    - {filepath}")
        print()
    
    print(f"{'='*70}")
    print(f"📊 SUMMARY")
    print(f"{'='*70}")
    print(f"Total duplicate sets: {len(duplicates)}")
    print(f"Total duplicate files: {duplicate_count}")
    print(f"Total wasted space: {format_size(total_wasted_space)}")
    print(f"{'='*70}\n")
    
    return total_wasted_space

def delete_duplicates(duplicates, keep_newest=True):
    """
    Delete duplicate files, keeping one copy
    
    Args:
        duplicates: Dictionary of duplicate file groups
        keep_newest: If True, keep the newest file; otherwise keep the first one
    """
    if not duplicates:
        return
    
    print(f"\n{'='*70}")
    print(f"🗑️  DELETING DUPLICATES")
    print(f"{'='*70}\n")
    
    deleted_count = 0
    freed_space = 0
    
    for file_hash, files in duplicates.items():
        if keep_newest:
            # Sort by modification time, newest first
            files.sort(key=lambda f: os.path.getmtime(f), reverse=True)
        
        keep_file = files[0]
        delete_files = files[1:]
        
        print(f"Keeping: {keep_file}")
        
        for filepath in delete_files:
            try:
                file_size = get_file_size(filepath)
                os.remove(filepath)
                print(f"  ✅ Deleted: {filepath}")
                deleted_count += 1
                freed_space += file_size
            except OSError as e:
                print(f"  ❌ Error deleting {filepath}: {e}")
        print()
    
    print(f"{'='*70}")
    print(f"✅ Deleted {deleted_count} duplicate files")
    print(f"💾 Freed {format_size(freed_space)} of space")
    print(f"{'='*70}\n")

def main():
    parser = argparse.ArgumentParser(description='Find and remove duplicate files')
    parser.add_argument('folder', nargs='?', default='.',
                        help='Folder to search (default: current directory)')
    parser.add_argument('--delete', action='store_true',
                        help='Delete duplicate files (keeps newest)')
    parser.add_argument('--no-recursive', action='store_true',
                        help='Do not search subdirectories')
    parser.add_argument('--keep-oldest', action='store_true',
                        help='Keep oldest file instead of newest (when deleting)')
    
    args = parser.parse_args()
    
    folder_path = os.path.expanduser(args.folder)
    
    if not os.path.exists(folder_path):
        print(f"❌ Error: Folder '{folder_path}' does not exist!")
        return
    
    duplicates = find_duplicates(folder_path, recursive=not args.no_recursive)
    display_duplicates(duplicates)
    
    if args.delete and duplicates:
        response = input("⚠️  Are you sure you want to delete duplicates? (yes/no): ")
        if response.lower() == 'yes':
            delete_duplicates(duplicates, keep_newest=not args.keep_oldest)
        else:
            print("❌ Deletion cancelled.")

if __name__ == "__main__":
    main()
