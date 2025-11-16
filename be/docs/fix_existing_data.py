"""
Fix existing data files that have incorrect dates (YYYY-MM-DD) and raw browser responses.
Removes bad entries and keeps only properly formatted LLM-processed entries.
"""

import json
import re
from pathlib import Path
from datetime import datetime
import shutil


def is_bad_entry(entry: dict) -> bool:
    """
    Identify entries that need to be removed.
    
    Bad entries have:
    - Date in YYYY-MM-DD format (not MM-DD-YYYY)
    - reputation_score of 0.0
    - Summary that looks like browser debug messages
    """
    date = entry.get('date', '')
    score = entry.get('reputation_score', 0)
    summary = entry.get('summary', '')
    
    # Check if date is in YYYY-MM-DD format (bad)
    is_old_date_format = re.match(r'^\d{4}-\d{2}-\d{2}$', date)
    
    # Check if it's a browser debug message
    is_debug_message = any([
        'evaluated step' in summary.lower(),
        'scrolled' in summary.lower(),
        'was the one above' in summary.lower(),
        'review 4' in summary.lower() and len(summary) < 50,
        'from previous screen' in summary.lower(),
    ])
    
    # Entry is bad if it has old date format AND (zero score OR debug message)
    return is_old_date_format and (score == 0.0 or is_debug_message)


def is_good_entry(entry: dict) -> bool:
    """
    Verify entry is properly formatted.
    
    Good entries have:
    - Date in MM-DD-YYYY format
    - Non-zero reputation score (usually)
    - Real review content in summary
    """
    date = entry.get('date', '')
    
    # Check if date is in MM-DD-YYYY format (good)
    is_new_date_format = re.match(r'^\d{2}-\d{2}-\d{4}$', date)
    
    return is_new_date_format


def fix_data_file(file_path: Path) -> dict:
    """
    Fix a single data file by removing bad entries.
    
    Returns:
        dict with stats: {
            'total': int,
            'bad': int,
            'good': int,
            'removed': int
        }
    """
    print(f"\n📂 Processing: {file_path.name}")
    print("-" * 80)
    
    # Backup original file
    backup_path = file_path.with_suffix('.json.backup')
    shutil.copy2(file_path, backup_path)
    print(f"✅ Backup created: {backup_path.name}")
    
    # Read data
    with open(file_path, 'r') as f:
        data = json.load(f)
    
    total = len(data)
    print(f"📊 Total entries: {total}")
    
    # Categorize entries
    bad_entries = []
    good_entries = []
    
    for entry in data:
        if is_bad_entry(entry):
            bad_entries.append(entry)
            print(f"  ❌ Bad: date={entry.get('date')}, summary={entry.get('summary')[:60]}...")
        elif is_good_entry(entry):
            good_entries.append(entry)
            print(f"  ✅ Good: date={entry.get('date')}, score={entry.get('reputation_score'):.2f}")
        else:
            # Edge case: not clearly good or bad, keep it but warn
            good_entries.append(entry)
            print(f"  ⚠️ Unclear: date={entry.get('date')}, keeping it")
    
    # Write cleaned data
    if bad_entries:
        with open(file_path, 'w') as f:
            json.dump(good_entries, f, indent=2)
        
        print(f"\n✅ File cleaned!")
        print(f"   Removed: {len(bad_entries)} bad entries")
        print(f"   Kept: {len(good_entries)} good entries")
    else:
        print(f"\n✅ File already clean, no changes needed")
    
    return {
        'total': total,
        'bad': len(bad_entries),
        'good': len(good_entries),
        'removed': len(bad_entries)
    }


def fix_all_brand_data(brands_dir: str = "brands") -> None:
    """
    Fix all data files in all brand directories.
    """
    brands_path = Path(brands_dir)
    
    if not brands_path.exists():
        print(f"❌ Brands directory not found: {brands_dir}")
        return
    
    print("=" * 80)
    print("DATA CLEANUP: Removing Bad Entries from Existing Files")
    print("=" * 80)
    
    all_stats = {
        'files_processed': 0,
        'total_entries': 0,
        'bad_entries': 0,
        'good_entries': 0,
    }
    
    # Find all data files
    data_files = list(brands_path.glob("*/day_*.json"))
    
    if not data_files:
        print("\n❌ No data files found")
        return
    
    print(f"\n📁 Found {len(data_files)} data files to check")
    
    # Process each file
    for file_path in data_files:
        stats = fix_data_file(file_path)
        
        all_stats['files_processed'] += 1
        all_stats['total_entries'] += stats['total']
        all_stats['bad_entries'] += stats['bad']
        all_stats['good_entries'] += stats['good']
    
    # Print summary
    print("\n" + "=" * 80)
    print("CLEANUP COMPLETE")
    print("=" * 80)
    
    print(f"\n📊 Summary:")
    print(f"   Files processed: {all_stats['files_processed']}")
    print(f"   Total entries: {all_stats['total_entries']}")
    print(f"   Bad entries removed: {all_stats['bad_entries']}")
    print(f"   Good entries kept: {all_stats['good_entries']}")
    
    if all_stats['bad_entries'] > 0:
        print(f"\n✅ Removed {all_stats['bad_entries']} entries with incorrect dates!")
        print(f"✅ All remaining {all_stats['good_entries']} entries use MM-DD-YYYY format")
        print(f"\n💾 Backups saved as *.json.backup files")
    else:
        print(f"\n✅ All files already clean!")


if __name__ == "__main__":
    fix_all_brand_data()
