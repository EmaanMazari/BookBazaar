"""
PostgreSQL Database and User Provisioning Script for BookBazaar
"""

import os
import sys
import secrets
from pathlib import Path
import psycopg2

BASE_DIR = Path(__file__).resolve().parent.parent

def setup_db():
    print("Connecting to PostgreSQL server as postgres...")
    conn = psycopg2.connect(dbname='postgres', user='postgres', host='127.0.0.1', port='5432')
    conn.autocommit = True
    cur = conn.cursor()

    # 1. Create or check database
    cur.execute("SELECT 1 FROM pg_catalog.pg_database WHERE datname = 'bookbazaar_db';")
    if not cur.fetchone():
        cur.execute("CREATE DATABASE bookbazaar_db ENCODING 'UTF8';")
        print("[OK] Database 'bookbazaar_db' created with UTF8 encoding.")
    else:
        print("[OK] Database 'bookbazaar_db' already exists.")

    # 2. Generate strong password
    db_pass = secrets.token_urlsafe(20)

    # 3. Create or update user
    cur.execute("SELECT 1 FROM pg_catalog.pg_roles WHERE rolname = 'bookbazaar_user';")
    if not cur.fetchone():
        cur.execute(f"CREATE USER bookbazaar_user WITH PASSWORD '{db_pass}';")
        print("[OK] User 'bookbazaar_user' created.")
    else:
        cur.execute(f"ALTER USER bookbazaar_user WITH PASSWORD '{db_pass}';")
        print("[OK] User 'bookbazaar_user' password updated.")

    cur.execute("ALTER DATABASE bookbazaar_db OWNER TO bookbazaar_user;")
    cur.execute("GRANT ALL PRIVILEGES ON DATABASE bookbazaar_db TO bookbazaar_user;")
    cur.close()
    conn.close()

    # 4. Grant schema privileges on bookbazaar_db
    conn2 = psycopg2.connect(dbname='bookbazaar_db', user='postgres', host='127.0.0.1', port='5432')
    conn2.autocommit = True
    cur2 = conn2.cursor()
    cur2.execute("GRANT ALL ON SCHEMA public TO bookbazaar_user;")
    cur2.execute("ALTER SCHEMA public OWNER TO bookbazaar_user;")
    cur2.close()
    conn2.close()
    print("[OK] Privileges granted to 'bookbazaar_user' on 'bookbazaar_db'.")

    # 5. Verify connecting as bookbazaar_user
    conn_verify = psycopg2.connect(
        dbname='bookbazaar_db',
        user='bookbazaar_user',
        password=db_pass,
        host='127.0.0.1',
        port='5432'
    )
    cur_v = conn_verify.cursor()
    cur_v.execute("SELECT current_user, current_database(), version();")
    u, db, v = cur_v.fetchone()
    print(f"[VERIFIED] Successfully connected as user '{u}' to database '{db}'.")
    conn_verify.close()

    # 6. Save credentials to .env
    env_file = BASE_DIR / '.env'
    lines = []
    if env_file.exists():
        with open(env_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()

    # Update or add keys
    env_updates = {
        'USE_POSTGRES': 'True',
        'DB_NAME': 'bookbazaar_db',
        'DB_USER': 'bookbazaar_user',
        'DB_PASSWORD': db_pass,
        'DB_HOST': '127.0.0.1',
        'DB_PORT': '5432'
    }

    new_lines = []
    seen = set()
    for line in lines:
        stripped = line.strip()
        if '=' in stripped and not stripped.startswith('#'):
            k = stripped.split('=', 1)[0].strip()
            if k in env_updates:
                new_lines.append(f"{k}={env_updates[k]}\n")
                seen.add(k)
                continue
        new_lines.append(line)

    for k, v in env_updates.items():
        if k not in seen:
            new_lines.append(f"{k}={v}\n")

    with open(env_file, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)

    print("[OK] .env updated with verified PostgreSQL credentials and USE_POSTGRES=True.")
    return True

if __name__ == '__main__':
    setup_db()
