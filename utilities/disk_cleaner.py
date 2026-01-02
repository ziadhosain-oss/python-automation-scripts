#!/usr/bin/env python3
"""
Disk Space Cleaner - Find and clean large/temporary files
Usage: python3 disk_cleaner.py [directory] [--clean]
"""

import os
import argparse
import shutil
from pathlib import Path
from datetime import datetime, timedelta

def get_size(bytes):
    """Convert bytes to human readable format"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes < 1024.0:
            return f"{bytes:.2f} {unit}"
        bytes /= 1024.0

def get_directory_size(path):
    """Calculate total size of directory"""
    total = 0
    try:
        for entry in os.scandir(path):
            if entry.is_file(follow_symlinks=False):
                total += entry.stat().st_size
            elif entry.is_dir(follow_symlinks=False):
                total += get_directory_size(entry.path)
    except (PermissionError, OSError):
        pass
    return total

def find_large_files(directory, min_size_mb=100, recursive=True):
    """Find files larger than specified size"""
    min_size = min_size_mb * 1024 * 1024  # Convert to bytes
    large_files = []
    
    print(f"🔍 Searching for files larger than {min_size_mb} MB...")
    
    try:
        if recursive:
            for root, dirs, files in os.walk(directory):
                for filename in files:
                    filepath = os.path.join(root, filename)
                    try:
                        size = os.path.getsize(filepath)
                        if size > min_size:
                            mtime = os.path.getmtime(filepath)
                            large_files.append((filepath, size, mtime))
                    except (OSError, PermissionError):
                        continue
        else:
            for entry in os.scandir(directory):
                if entry.is_file():
                    try:
                        size = entry.stat().st_size
                        if size > min_size:
                            mtime = entry.stat().st_mtime
                            large_files.append((entry.path, size, mtime))
                    except (OSError, PermissionError):
                        continue
    except (PermissionError, OSError) as e:
        print(f"⚠️  Error accessing directory: {e}")
    
    return large_files

def find_temp_files(directory):
    """Find temporary and cache files"""
    temp_patterns = [
        '.tmp', '.temp', '.cache', '~', '.bak', '.old',
        '__pycache__', '.pyc', 'Thumbs.db', '.DS_Store'
    ]
    
    temp_files = []
    
    print(f"🔍 Searching for temporary files...")
    
    try:
        for root, dirs, files in os.walk(directory):
            # Check for cache directories
            if any(pattern in root for pattern in ['__pycache__', '.cache', 'Cache']):
                size = get_directory_size(root)
                if size > 0:
                    temp_files.append((root, size, os.path.getmtime(root), True))
            
            for filename in files:
                if any(filename.endswith(pattern) or pattern in filename for pattern in temp_patterns):
                    filepath = os.path.join(root, filename)
                    try:
                        size = os.path.getsize(filepath)
                        mtime = os.path.getmtime(filepath)
                        temp_files.append((filepath, size, mtime, False))
                    except (OSError, PermissionError):
                        continue
    except (PermissionError, OSError) as e:
        print(f"⚠️  Error accessing directory: {e}")
    
    return temp_files

def find_old_files(directory, days=90):
    """Find files not accessed in specified days"""
    cutoff_date = datetime.now() - timedelta(days=days)
    old_files = []
    
    print(f"🔍 Searching for files not accessed in {days} days...")
    
    try:
        for root, dirs, files in os.walk(directory):
            for filename in files:
                filepath = os.path.join(root, filename)
                try:
                    atime = os.path.getatime(filepath)
                    if datetime.fromtimestamp(atime) < cutoff_date:
                        size = os.path.getsize(filepath)
                        old_files.append((filepath, size, atime))
                except (OSError, PermissionError):
                    continue
    except (PermissionError, OSError) as e:
        print(f"⚠️  Error accessing directory: {e}")
    
    return old_files

def analyze_disk(directory, min_size_mb=100, old_days=90):
    """Analyze disk usage and find cleanable files"""
    directory = os.path.expanduser(directory)
    
    if not os.path.exists(directory):
        print(f"❌ Error: Directory '{directory}' does not exist!")
        return None
    
    print(f"\n{'='*70}")
    print(f"💿 DISK SPACE ANALYSIS")
    print(f"{'='*70}")
    print(f"Analyzing: {directory}\n")
    
    # Current disk usage
    try:
        total, used, free = shutil.disk_usage(directory)
        print(f"Total Space: {get_size(total)}")
        print(f"Used Space: {get_size(used)} ({used/total*100:.1f}%)")
        print(f"Free Space: {get_size(free)} ({free/total*100:.1f}%)")
        print(f"\n{'='*70}\n")
    except OSError as e:
        print(f"⚠️  Could not get disk usage: {e}\n")
    
    # Find large files
    large_files = find_large_files(directory, min_size_mb)
    
    # Find temporary files
    temp_files = find_temp_files(directory)
    
    # Find old files
    old_files = find_old_files(directory, old_days)
    
    return {
        'large_files': large_files,
        'temp_files': temp_files,
        'old_files': old_files
    }

def display_results(results):
    """Display analysis results"""
    if not results:
        return
    
    # Large files
    if results['large_files']:
        print(f"\n{'='*70}")
        print(f"📊 LARGE FILES (sorted by size)")
        print(f"{'='*70}\n")
        
        large_files = sorted(results['large_files'], key=lambda x: x[1], reverse=True)
        total_size = sum(f[1] for f in large_files)
        
        for filepath, size, mtime in large_files[:20]:  # Show top 20
            date_str = datetime.fromtimestamp(mtime).strftime('%Y-%m-%d')
            print(f"📁 {get_size(size):>12} - {date_str} - {filepath}")
        
        if len(large_files) > 20:
            print(f"\n... and {len(large_files) - 20} more files")
        
        print(f"\nTotal: {len(large_files)} files, {get_size(total_size)}")
    else:
        print(f"\n✅ No large files found")
    
    # Temporary files
    if results['temp_files']:
        print(f"\n{'='*70}")
        print(f"🗑️  TEMPORARY FILES & CACHE")
        print(f"{'='*70}\n")
        
        total_size = sum(f[1] for f in results['temp_files'])
        
        for filepath, size, mtime, is_dir in results['temp_files'][:20]:
            item_type = "DIR" if is_dir else "FILE"
            print(f"🗑️  {get_size(size):>12} - {item_type:>4} - {filepath}")
        
        if len(results['temp_files']) > 20:
            print(f"\n... and {len(results['temp_files']) - 20} more items")
        
        print(f"\nTotal: {len(results['temp_files'])} items, {get_size(total_size)}")
    else:
        print(f"\n✅ No temporary files found")
    
    # Old files
    if results['old_files']:
        print(f"\n{'='*70}")
        print(f"📅 OLD/UNUSED FILES")
        print(f"{'='*70}\n")
        
        old_files = sorted(results['old_files'], key=lambda x: x[2])
        total_size = sum(f[1] for f in old_files)
        
        for filepath, size, atime in old_files[:20]:
            date_str = datetime.fromtimestamp(atime).strftime('%Y-%m-%d')
            print(f"📁 {get_size(size):>12} - Last access: {date_str} - {filepath}")
        
        if len(old_files) > 20:
            print(f"\n... and {len(old_files) - 20} more files")
        
        print(f"\nTotal: {len(old_files)} files, {get_size(total_size)}")
    else:
        print(f"\n✅ No old files found")
    
    print(f"\n{'='*70}\n")

def clean_temp_files(temp_files):
    """Delete temporary files"""
    if not temp_files:
        print("No temporary files to clean")
        return
    
    print(f"\n{'='*70}")
    print(f"🧹 CLEANING TEMPORARY FILES")
    print(f"{'='*70}\n")
    
    deleted_count = 0
    freed_space = 0
    
    for filepath, size, mtime, is_dir in temp_files:
        try:
            if is_dir:
                shutil.rmtree(filepath)
                print(f"✅ Deleted directory: {filepath}")
            else:
                os.remove(filepath)
                print(f"✅ Deleted: {filepath}")
            
            deleted_count += 1
            freed_space += size
        except (OSError, PermissionError) as e:
            print(f"❌ Error deleting {filepath}: {e}")
    
    print(f"\n{'='*70}")
    print(f"✅ Deleted {deleted_count} items")
    print(f"💾 Freed {get_size(freed_space)} of space")
    print(f"{'='*70}\n")

def main():
    parser = argparse.ArgumentParser(description='Analyze and clean disk space')
    parser.add_argument('directory', nargs='?', default='~',
                        help='Directory to analyze (default: home directory)')
    parser.add_argument('--min-size', type=int, default=100,
                        help='Minimum file size in MB for large files (default: 100)')
    parser.add_argument('--old-days', type=int, default=90,
                        help='Consider files older than N days as old (default: 90)')
    parser.add_argument('--clean-temp', action='store_true',
                        help='Clean temporary files and cache')
    
    args = parser.parse_args()
    
    results = analyze_disk(args.directory, args.min_size, args.old_days)
    
    if results:
        display_results(results)
        
        if args.clean_temp:
            response = input("⚠️  Clean temporary files? This cannot be undone! (yes/no): ")
            if response.lower() == 'yes':
                clean_temp_files(results['temp_files'])
            else:
                print("❌ Cleaning cancelled")

if __name__ == "__main__":
    main()
