#!/usr/bin/env python3
"""
Test script to demonstrate FoxNest storage optimizations
"""

import os
import sys
from pathlib import Path

def get_dir_size(path):
    """Calculate total size of directory"""
    total = 0
    try:
        for entry in os.scandir(path):
            if entry.is_file():
                total += entry.stat().st_size
            elif entry.is_dir():
                total += get_dir_size(entry.path)
    except Exception as e:
        print(f"Error: {e}")
    return total

def format_size(bytes_size):
    """Format bytes to human readable"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.2f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.2f} TB"

def analyze_fox_directory():
    """Analyze .fox directory structure and size"""
    fox_dir = Path(".fox")
    
    if not fox_dir.exists():
        print("Error: Not a Fox repository (no .fox directory found)")
        print("Run 'fox init' first")
        return
    
    print("=" * 60)
    print("FoxNest Repository Storage Analysis")
    print("=" * 60)
    print()
    
    # Analyze components
    components = {
        "objects": fox_dir / "objects",
        "packs": fox_dir / "packs",
        "staging": fox_dir / "staging",
        "commits.json": fox_dir / "commits.json",
        "config.json": fox_dir / "config.json",
        "index.json": fox_dir / "index.json",
        "delta_cache.json": fox_dir / "delta_cache.json",
    }
    
    total_size = 0
    
    print("Storage Breakdown:")
    print("-" * 60)
    
    for name, path in components.items():
        if path.exists():
            if path.is_dir():
                size = get_dir_size(path)
                # Count files
                file_count = sum(1 for _ in path.rglob("*") if _.is_file())
                print(f"{name:20} {format_size(size):>12}  ({file_count} files)")
            else:
                size = path.stat().st_size
                print(f"{name:20} {format_size(size):>12}")
            total_size += size
        else:
            print(f"{name:20} {'<not found>':>12}")
    
    print("-" * 60)
    print(f"{'TOTAL':20} {format_size(total_size):>12}")
    print()
    
    # Compression analysis
    objects_dir = fox_dir / "objects"
    packs_dir = fox_dir / "packs"
    
    if objects_dir.exists():
        loose_objects = sum(1 for _ in objects_dir.rglob("*") if _.is_file())
        print(f"Loose objects: {loose_objects}")
    
    if packs_dir.exists():
        pack_files = list(packs_dir.glob("*.pack"))
        if pack_files:
            print(f"Pack files: {len(pack_files)}")
            for pack in pack_files:
                print(f"  - {pack.name}: {format_size(pack.stat().st_size)}")
        else:
            print("Pack files: 0 (run 'fox gc' to create packs)")
    
    print()
    
    # Recommendations
    if loose_objects > 20:
        print("💡 Recommendation: Run 'fox gc' to pack loose objects")
        print("   This will reduce storage and improve performance")
    elif loose_objects > 0:
        print("✅ Repository is well optimized")
    else:
        print("✅ All objects are packed efficiently")
    
    print()
    print("=" * 60)

if __name__ == "__main__":
    analyze_fox_directory()
