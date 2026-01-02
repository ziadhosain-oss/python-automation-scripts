Python Automation & System Scripts

A collection of Python scripts for automating system tasks and workflows. These tools help you manage files, monitor system health, find duplicates, create backups, and clean up disk space.

📋 Features

🗂️ File Operations
- File Organizer - Automatically organize files by type into categorized folders
- Duplicate Finder - Find and remove duplicate files to save disk space

💻 System Monitoring
- System Health Monitor - Monitor CPU, memory, disk usage, and running processes
- Disk Space Cleaner - Find and clean large files, temporary files, and old unused files

💾 Data Management
- Automated Backup Tool - Create compressed backups of important directories

🚀 Installation

1. Clone the repository
`bash
git clone https://github.com/ziadhosain-oss/python-automation-scripts.git
cd python-automation-scripts
`

2. Install dependencies
`bash
pip3 install -r requirements.txt
`

Or install system-wide on Ubuntu:
`bash
sudo apt install python3-psutil
`

📖 Usage

File Organizer
Organize messy folders by automatically sorting files into categories:

`bash

Organize Downloads folder
python3 fileoperations/fileorganizer.py ~/Downloads

Dry run (preview without moving files)
python3 fileoperations/fileorganizer.py ~/Downloads --dry-run

Organize current directory
python3 fileoperations/fileorganizer.py .
`

Categories: Images, Documents, Videos, Audio, Archives, Code, Executables, Books

System Health Monitor
Monitor your system's health and resource usage:

`bash

Single check
python3 systemmonitoring/systemmonitor.py

Continuous monitoring (refresh every 5 seconds)
python3 systemmonitoring/systemmonitor.py --continuous

Custom refresh interval
python3 systemmonitoring/systemmonitor.py -c -i 10
`

Monitors: CPU usage, memory (RAM & swap), disk space, network stats, battery status, top processes

Duplicate File Finder
Find and remove duplicate files:

`bash

Find duplicates in current directory
python3 utilities/duplicate_finder.py .

Find duplicates recursively in a folder
python3 utilities/duplicate_finder.py ~/Documents

Find and delete duplicates (keeps newest)
python3 utilities/duplicate_finder.py ~/Downloads --delete

Non-recursive search
python3 utilities/duplicate_finder.py . --no-recursive
`

Automated Backup Tool
Create compressed backups of important files:

`bash

Backup Documents folder (default)
python3 dataprocessing/backuptool.py

Backup specific folder
python3 dataprocessing/backuptool.py ~/Projects ~/Backups

Use tar.gz compression
python3 dataprocessing/backuptool.py ~/Projects ~/Backups --format tar.gz

Exclude patterns
python3 dataprocessing/backuptool.py ~/Code ~/Backups --exclude nodemodules .git pycache_

List existing backups
python3 dataprocessing/backuptool.py --list
`

Disk Space Cleaner
Analyze disk usage and clean up space:

`bash

Analyze home directory
python3 utilities/disk_cleaner.py ~

Find files larger than 500MB
python3 utilities/disk_cleaner.py ~ --min-size 500

Find files not accessed in 180 days
python3 utilities/disk_cleaner.py ~ --old-days 180

Clean temporary files (interactive)
python3 utilities/disk_cleaner.py ~ --clean-temp
`

Finds: Large files, temporary/cache files, old unused files

📁 Project Structure

`
python-automation-scripts/
├── file_operations/
│   └── file_organizer.py          # Organize files by type
├── system_monitoring/
│   └── system_monitor.py          # Monitor system health
├── data_processing/
│   └── backup_tool.py             # Create automated backups
├── utilities/
│   ├── duplicate_finder.py        # Find duplicate files
│   └── disk_cleaner.py           # Clean disk space
├── requirements.txt               # Python dependencies
└── README.md                      # This file
`

⚙️ Requirements

- Python 3.6+
- Ubuntu/Linux (tested on Ubuntu)
- Required packages: psutil

🔒 Safety Features

- Dry run mode for file operations
- Confirmation prompts before deleting files
- Error handling for permission issues
- Duplicate detection prevents accidental file loss
- Backup verification ensures data integrity

💡 Tips

1. Test with dry run first: Always use --dry-run when trying new commands
2. Start small: Test scripts on small folders before running on entire system
3. Regular backups: Set up automated backups using cron jobs
4. Monitor system: Run system monitor to track resource usage over time
5. Clean regularly: Schedule disk cleaning to maintain optimal performance

🤝 Contributing

Contributions are welcome! Feel free to:
- Report bugs
- Suggest new features
- Submit pull requests
- Improve documentation

📝 License

This project is open source and available under the MIT License.

⚠️ Disclaimer

These scripts modify files and system settings. Always:
- Review what the scripts will do before running them
- Keep backups of important data
- Test on non-critical files first
- Use at your own risk

📬 Contact

Created by @ziadhosain-oss

---

Happy Automating! 🚀
