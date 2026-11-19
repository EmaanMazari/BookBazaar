#!/usr/bin/env bash
# ========================================================
# BookBazaar Pakistan - Automated PostgreSQL Backup Script
# Usage: ./deploy/postgres_backup.sh
# Add to crontab: 0 2 * * * /var/www/bookbazaar/deploy/postgres_backup.sh >> /var/log/bookbazaar/backup.log 2>&1
# ========================================================

set -euo pipefail

BACKUP_DIR="/var/backups/bookbazaar"
DATE=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="${BACKUP_DIR}/bookbazaar_db_${DATE}.sql.gz"
RETENTION_DAYS=7

mkdir -p "${BACKUP_DIR}"

# Database credentials (can also be read from /var/www/bookbazaar/.env)
DB_NAME="${DB_NAME:-bookbazaar_db}"
DB_USER="${DB_USER:-bookbazaar_user}"
DB_HOST="${DB_HOST:-127.0.0.1}"
DB_PORT="${DB_PORT:-5432}"

echo "[$(date)] Starting PostgreSQL backup for ${DB_NAME}..."

# Execute pg_dump and pipe through gzip
PGPASSWORD="${DB_PASSWORD:-}" pg_dump -h "${DB_HOST}" -p "${DB_PORT}" -U "${DB_USER}" -d "${DB_NAME}" -F p | gzip -9 > "${BACKUP_FILE}"

FILE_SIZE=$(du -h "${BACKUP_FILE}" | cut -f1)
echo "[$(date)] Backup successfully generated: ${BACKUP_FILE} (${FILE_SIZE})"

# Prune old backups exceeding retention period
echo "[$(date)] Cleaning up backups older than ${RETENTION_DAYS} days..."
find "${BACKUP_DIR}" -name "bookbazaar_db_*.sql.gz" -type f -mtime +${RETENTION_DAYS} -delete

echo "[$(date)] PostgreSQL backup routine completed successfully."
