"""
BookLoop Database Backup and Restore Utility
Department of Software Engineering, The Islamia University of Bahawalpur (IUB)
"""

import os
import sys
import shutil
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bookbazaar_backend.settings')
django.setup()

from django.core.management import call_command
from django.contrib.auth.models import User
from bazaar.models import (
    UserProfile, Book, Listing, ContactUnlock,
    SellerReview, Favorite, Advertisement, PlatformSetting
)

def print_record_counts():
    print("\n--- Current Database Record Counts ---")
    print(f"Users (Auth):      {User.objects.count()}")
    print(f"User Profiles:     {UserProfile.objects.count()}")
    print(f"Books Catalog:     {Book.objects.count()}")
    print(f"Listings:          {Listing.objects.count()} (Active: {Listing.objects.filter(status='active').count()}, Sold: {Listing.objects.filter(status='sold').count()})")
    print(f"Contact Unlocks:   {ContactUnlock.objects.count()}")
    print(f"Seller Reviews:    {SellerReview.objects.count()}")
    print(f"Favorites:         {Favorite.objects.count()}")
    print(f"Advertisements:    {Advertisement.objects.count()}")
    print(f"Platform Settings: {PlatformSetting.objects.count()}")
    print("--------------------------------------\n")

def backup_sqlite():
    db_file = BASE_DIR / 'db.sqlite3'
    if not db_file.exists():
        print(f"Error: {db_file} does not exist.")
        return False

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = BASE_DIR / f'db.sqlite3.backup_{timestamp}'
    shutil.copy2(db_file, backup_path)
    print(f"[OK] Binary backup created: {backup_path.name} ({backup_path.stat().st_size} bytes)")

    # Also dump UTF-8 JSON fixture
    json_path = BASE_DIR / f'datadump_{timestamp}.json'
    with open(json_path, 'w', encoding='utf-8') as f:
        call_command('dumpdata', '--natural-foreign', '--natural-primary', exclude=['contenttypes', 'auth.permission'], stdout=f)
    print(f"[OK] JSON UTF-8 fixture created: {json_path.name} ({json_path.stat().st_size} bytes)")

    # Ensure datadump_utf8.json is also updated as standard reference
    standard_dump = BASE_DIR / 'datadump_utf8.json'
    shutil.copy2(json_path, standard_dump)
    print(f"[OK] Standard fixture updated: {standard_dump.name}")
    return True

def restore_from_json(json_filename='datadump_utf8.json'):
    json_path = BASE_DIR / json_filename
    if not json_path.exists():
        print(f"Error: {json_path} does not exist.")
        return False

    print(f"Restoring database from {json_path.name}...")
    call_command('loaddata', str(json_path))
    print("[OK] Restore completed successfully.")
    print_record_counts()
    return True

if __name__ == '__main__':
    mode = sys.argv[1] if len(sys.argv) > 1 else 'backup'
    print_record_counts()
    if mode == 'backup':
        backup_sqlite()
    elif mode == 'restore':
        json_file = sys.argv[2] if len(sys.argv) > 2 else 'datadump_utf8.json'
        restore_from_json(json_file)
    elif mode == 'counts':
        pass
    else:
        print(f"Unknown command '{mode}'. Usage: python db_backup_restore.py [backup|restore|counts]")
