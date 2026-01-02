    #!/usr/bin/env python3
"""
File Organizer - Automatically organize files by type
Usage: python3 file_organizer.py [folder_path]
"""

import os
import shutil
import argparse
from pathlib import Path
from datetime import datetime

# File type categories
FILE_TYPES = {
    'Images': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.ico', '.webp'],
    'Documents': ['.pdf', '.doc', '.docx', '.txt', '.xlsx', '.xls', '.pptx', '.odt', '.csv'],
    'Videos': ['.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm'],
    'Audio': ['.mp3', '.wav', '.flac', '.m4a', '.aac', '.ogg', '.wma'],
    'Archives': ['.zip', '.rar', '.7z', '.tar', '.gz', '.bz2', '.xz'],
    'Code': ['.py', '.js', '.html', '.css', '.java', '.cpp', '.c', '.h', '.sh', '.json', '.xml'],
    'Executables': ['.exe', '.msi', '.deb', '.rpm', '.appimage'],
    'Books': ['.epub', '.mobi', '.azw', '.azw3']
}

def organize_files(folder_path, dry_run=False):
    """
    Organize files in the specified folder by type
    
    Args:
        folder_path: Path to folder to organize
        dry_run: If True, only show what would be done without moving files
    """
    folder_path = os.path.expanduser(folder_path)
    
    if not os.path.exists(folder_path):
        print(f"❌ Error: Folder '{folder_path}' does not exist!")
        return
    
    print(f"\n{'='*60}")
    print(f"📁 Organizing files in: {folder_path}")
    print(f"{'='*60}\n")
    
    if dry_run:
        print("🔍 DRY RUN MODE - No files will be moved\n")
    
    # Create category folders
    for category in FILE_TYPES.keys():
        category_path = os.path.join(folder_path, category)
        if not dry_run and not os.path.exists(category_path):
            os.makedirs(category_path)
            print(f"✅ Created folder: {category}")
    
    # Track statistics
    stats = {category: 0 for category in FILE_TYPES.keys()}
    stats['Unknown'] = 0
    stats['Skipped'] = 0
    
    # Process files
    for item in os.listdir(folder_path):
        item_path = os.path.join(folder_path, item)
        
        # Skip directories
        if os.path.isdir(item_path):
            continue
        
        # Get file extension
        file_ext = Path(item).suffix.lower()
        
        # Find appropriate category
        moved = False
        for category, extensions in FILE_TYPES.items():
            if file_ext in extensions:
                dest_folder = os.path.join(folder_path, category)
                dest_path = os.path.join(dest_folder, item)
                
                # Handle duplicate filenames
                if os.path.exists(dest_path):
                    base, ext = os.path.splitext(item)
                    counter = 1
                    while os.path.exists(dest_path):
                        new_name = f"{base}_{counter}{ext}"
                        dest_path = os.path.join(dest_folder, new_name)
                        counter += 1
                
                if not dry_run:
                    shutil.move(item_path, dest_path)
                
                print(f"📄 {item} → {category}/")
                stats[category] += 1
                moved = True
                break
        
        if not moved:
            if file_ext:
                print(f"❓ {item} (unknown type: {file_ext})")
                stats['Unknown'] += 1
            else:
                print(f"⏭️  Skipped: {item} (no extension)")
                stats['Skipped'] += 1
    
    # Print summary
    print(f"\n{'='*60}")
    print("📊 SUMMARY")
    print(f"{'='*60}")
    for category, count in stats.items():
        if count > 0:
            print(f"{category}: {count} files")
    print(f"{'='*60}\n")
    
    if dry_run:
        print("ℹ️  This was a dry run. Run without --dry-run to actually move files.")
    else:
        print("✅ Organization complete!")

def main():
    parser = argparse.ArgumentParser(description='Organize files by type')
    parser.add_argument('folder', nargs='?', default='~/Downloads',
                        help='Folder to organize (default: ~/Downloads)')
    parser.add_argument('--dry-run', action='store_true',
                        help='Show what would be done without moving files')
    
    args = parser.parse_args()
    organize_files(args.folder, args.dry_run)

if __name__ == "__main__":
    main()
