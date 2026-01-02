#!/usr/bin/env python3
"""
System Health Monitor - Monitor CPU, Memory, Disk, and Network
Usage: python3 system_monitor.py [--continuous] [--interval SECONDS]
"""

import psutil
import time
import argparse
from datetime import datetime

def get_size(bytes):
    """Convert bytes to human readable format"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes < 1024.0:
            return f"{bytes:.2f} {unit}"
        bytes /= 1024.0

def check_system_health():
    """Check and display system health metrics"""
    print(f"\n{'='*70}")
    print(f"🖥️  SYSTEM HEALTH CHECK - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*70}\n")
    
    # CPU Information
    print("💻 CPU USAGE")
    print("-" * 70)
    cpu_percent = psutil.cpu_percent(interval=1, percpu=False)
    cpu_count = psutil.cpu_count()
    cpu_freq = psutil.cpu_freq()
    
    print(f"Overall Usage: {cpu_percent}%")
    print(f"Physical Cores: {psutil.cpu_count(logical=False)}")
    print(f"Total Cores: {cpu_count}")
    if cpu_freq:
        print(f"Current Frequency: {cpu_freq.current:.2f} MHz")
    
    # Alert for high CPU
    if cpu_percent > 80:
        print("⚠️  WARNING: High CPU usage detected!")
    
    # Memory Information
    print(f"\n💾 MEMORY USAGE")
    print("-" * 70)
    memory = psutil.virtual_memory()
    swap = psutil.swap_memory()
    
    print(f"Total RAM: {get_size(memory.total)}")
    print(f"Available: {get_size(memory.available)} ({100 - memory.percent:.1f}%)")
    print(f"Used: {get_size(memory.used)} ({memory.percent:.1f}%)")
    print(f"Swap Total: {get_size(swap.total)}")
    print(f"Swap Used: {get_size(swap.used)} ({swap.percent:.1f}%)")
    
    # Alert for high memory
    if memory.percent > 80:
        print("⚠️  WARNING: High memory usage detected!")
    if swap.percent > 50:
        print("⚠️  WARNING: High swap usage detected!")
    
    # Disk Information
    print(f"\n💿 DISK USAGE")
    print("-" * 70)
    partitions = psutil.disk_partitions()
    for partition in partitions:
        try:
            usage = psutil.disk_usage(partition.mountpoint)
            print(f"\nDevice: {partition.device}")
            print(f"  Mountpoint: {partition.mountpoint}")
            print(f"  File system: {partition.fstype}")
            print(f"  Total: {get_size(usage.total)}")
            print(f"  Used: {get_size(usage.used)} ({usage.percent}%)")
            print(f"  Free: {get_size(usage.free)}")
            
            # Alert for low disk space
            if usage.percent > 80:
                print(f"  ⚠️  WARNING: Low disk space on {partition.mountpoint}!")
        except PermissionError:
            continue
    
    # Network Information
    print(f"\n🌐 NETWORK STATS")
    print("-" * 70)
    net_io = psutil.net_io_counters()
    print(f"Bytes Sent: {get_size(net_io.bytes_sent)}")
    print(f"Bytes Received: {get_size(net_io.bytes_recv)}")
    print(f"Packets Sent: {net_io.packets_sent:,}")
    print(f"Packets Received: {net_io.packets_recv:,}")
    
    # Battery Information (if available)
    battery = psutil.sensors_battery()
    if battery:
        print(f"\n🔋 BATTERY STATUS")
        print("-" * 70)
        print(f"Percentage: {battery.percent}%")
        print(f"Plugged in: {'Yes' if battery.power_plugged else 'No'}")
        if not battery.power_plugged:
            hours, remainder = divmod(battery.secsleft, 3600)
            minutes = remainder // 60
            print(f"Time remaining: {int(hours)}h {int(minutes)}m")
    
    # Process Information
    print(f"\n⚙️  TOP 5 PROCESSES BY CPU")
    print("-" * 70)
    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent']):
        try:
            processes.append(proc.info)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    
    processes.sort(key=lambda x: x['cpu_percent'] or 0, reverse=True)
    for i, proc in enumerate(processes[:5], 1):
        print(f"{i}. {proc['name'][:30]:<30} - CPU: {proc['cpu_percent']:.1f}%")
    
    print(f"\n⚙️  TOP 5 PROCESSES BY MEMORY")
    print("-" * 70)
    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'memory_percent']):
        try:
            processes.append(proc.info)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    
    processes.sort(key=lambda x: x['memory_percent'] or 0, reverse=True)
    for i, proc in enumerate(processes[:5], 1):
        print(f"{i}. {proc['name'][:30]:<30} - MEM: {proc['memory_percent']:.1f}%")
    
    print(f"\n{'='*70}\n")

def continuous_monitor(interval):
    """Continuously monitor system health"""
    print(f"🔄 Starting continuous monitoring (refresh every {interval} seconds)")
    print("Press Ctrl+C to stop...\n")
    
    try:
        while True:
            check_system_health()
            time.sleep(interval)
    except KeyboardInterrupt:
        print("\n\n✅ Monitoring stopped.")

def main():
    parser = argparse.ArgumentParser(description='Monitor system health')
    parser.add_argument('--continuous', '-c', action='store_true',
                        help='Continuously monitor system')
    parser.add_argument('--interval', '-i', type=int, default=5,
                        help='Refresh interval in seconds (default: 5)')
    
    args = parser.parse_args()
    
    if args.continuous:
        continuous_monitor(args.interval)
    else:
        check_system_health()

if __name__ == "__main__":
    main()
