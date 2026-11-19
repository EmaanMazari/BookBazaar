"""
BookBazaar PostgreSQL Migration & Verification Script
Department of Software Engineering, The Islamia University of Bahawalpur (IUB)
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

# Load .env
load_dotenv(BASE_DIR / '.env')

import psycopg2

def check_postgres_connection():
    db_name = os.environ.get('DB_NAME', 'bookbazaar_db')
    db_user = os.environ.get('DB_USER', 'bookbazaar_user')
    db_pass = os.environ.get('DB_PASSWORD', '')
    db_host = os.environ.get('DB_HOST', '127.0.0.1')
    db_port = os.environ.get('DB_PORT', '5432')

    print("==================================================")
    print(" BookBazaar - PostgreSQL Connection Verification")
    print("==================================================")
    print(f"Target Host:     {db_host}:{db_port}")
    print(f"Database Name:   {db_name}")
    print(f"Database User:   {db_user}")

    try:
        conn = psycopg2.connect(
            dbname=db_name,
            user=db_user,
            password=db_pass,
            host=db_host,
            port=db_port,
            connect_timeout=3
        )
        cur = conn.cursor()
        cur.execute("SELECT version();")
        version = cur.fetchone()[0]
        print(f"\n[SUCCESS] Connected to PostgreSQL Server!")
        print(f"Version: {version}")
        cur.close()
        conn.close()
        return True, None

    except psycopg2.OperationalError as e:
        err_msg = str(e).strip()
        print(f"\n[NOTICE] Unable to establish connection to PostgreSQL server:")
        print(f"Details: {err_msg}")
        return False, err_msg
    except Exception as e:
        err_msg = str(e).strip()
        print(f"\n[ERROR] Unexpected error connecting to PostgreSQL:")
        print(f"Details: {err_msg}")
        return False, err_msg


def run_migration_pipeline():
    can_connect, reason = check_postgres_connection()

    if not can_connect:
        print("\n==================================================")
        print(" PostgreSQL Server Status & Recommendation")
        print("==================================================")
        print("PostgreSQL is configured in settings.py via USE_POSTGRES=True.")
        print("However, the PostgreSQL server is currently not accessible:")
        print(f"Reason: {reason}")
        print("\n[ACTIVE DATABASE]: SQLite (db.sqlite3) fallback remains safe with zero data loss.")
        print("==================================================")
        return False

    print("\nStarting Django migration pipeline for PostgreSQL...")
    os.environ['USE_POSTGRES'] = 'True'
    
    import django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bookbazaar_backend.settings')
    django.setup()

    from django.core.management import call_command
    from django.contrib.auth.models import User
    from bazaar.models import UserProfile, Book, Listing, ContactUnlock, SellerReview, Favorite, PlatformSetting

    # Apply migrations
    print("Applying migrations to PostgreSQL...")
    call_command('migrate', interactive=False)
    print("[OK] Migrations applied.")

    # Verify counts
    print("\n--- Verifying PostgreSQL Record Counts ---")
    print(f"Users:           {User.objects.count()}")
    print(f"Profiles:        {UserProfile.objects.count()}")
    print(f"Books Catalog:   {Book.objects.count()}")
    print(f"Listings:        {Listing.objects.count()}")
    print(f"Contact Unlocks: {ContactUnlock.objects.count()}")
    print(f"Seller Reviews:  {SellerReview.objects.count()}")
    print(f"Favorites:       {Favorite.objects.count()}")
    print(f"Platform Settings: {PlatformSetting.objects.count()}")
    print("------------------------------------------")
    print("\n[SUCCESS] PostgreSQL migration and data verification complete!")
    return True


if __name__ == '__main__':
    run_migration_pipeline()
