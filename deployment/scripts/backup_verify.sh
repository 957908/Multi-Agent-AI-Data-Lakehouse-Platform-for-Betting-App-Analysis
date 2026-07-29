#!/bin/bash
# ==============================================================================
# Script: backup_verify.sh
# Purpose: Automatically runs postgres backups and validates restore integrity.
# Author: Radhika Patil – Senior DevOps Engineer
# Project: SentinelX Trust AI
# ==============================================================================

set -eo pipefail

BACKUP_DIR="./backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="${BACKUP_DIR}/sentinelx_db_${TIMESTAMP}.sql"
LOG_FILE="${BACKUP_DIR}/backup_verify_${TIMESTAMP}.log"

mkdir -p "${BACKUP_DIR}"

echo "======================================================================" | tee -a "${LOG_FILE}"
echo "SentinelX Trust AI - Starting Backup & Restore Validation Loop" | tee -a "${LOG_FILE}"
echo "Timestamp: $(date)" | tee -a "${LOG_FILE}"
echo "======================================================================" | tee -a "${LOG_FILE}"

# Step 1: Run pg_dump inside the active PostgreSQL container
echo "[1/4] Running pg_dump against sentinelx-postgres..." | tee -a "${LOG_FILE}"
if ! docker exec sentinelx-postgres pg_dump -U postgres sentinelx_trust_ai > "${BACKUP_FILE}" 2>> "${LOG_FILE}"; then
    echo "❌ ERROR: Database backup failed!" | tee -a "${LOG_FILE}"
    exit 1
fi
echo "✅ SUCCESS: Database backup written to ${BACKUP_FILE} ($(du -sh "${BACKUP_FILE}" | cut -f1))" | tee -a "${LOG_FILE}"

# Step 2: Spin up a temporary PostgreSQL instance for verification
echo "[2/4] Launching validation container..." | tee -a "${LOG_FILE}"
VALIDATION_CONTAINER="sentinelx-postgres-validation-${TIMESTAMP}"
docker run --name "${VALIDATION_CONTAINER}" \
  -e POSTGRES_PASSWORD=validation_password \
  -e POSTGRES_DB=sentinelx_trust_ai_validation \
  -d postgres:16-alpine > /dev/null

# Cleanup handler to ensure temporary container is removed on exit
cleanup() {
    echo "[Cleanup] Removing validation container..."
    docker rm -f "${VALIDATION_CONTAINER}" > /dev/null 2>&1 || true
}
trap cleanup EXIT

# Wait for validation PostgreSQL to be ready
echo "Waiting for validation PostgreSQL to boot..." | tee -a "${LOG_FILE}"
for i in {1..30}; do
    if docker exec "${VALIDATION_CONTAINER}" pg_isready -U postgres >/dev/null 2>&1; then
        break
    fi
    sleep 1
done

if ! docker exec "${VALIDATION_CONTAINER}" pg_isready -U postgres >/dev/null 2>&1; then
    echo "❌ ERROR: Validation container failed to start in time!" | tee -a "${LOG_FILE}"
    exit 1
fi
echo "✅ SUCCESS: Validation container healthy." | tee -a "${LOG_FILE}"

# Step 3: Restore the backup file to the temporary database
echo "[3/4] Restoring backup to verification container..." | tee -a "${LOG_FILE}"
if ! docker exec -i "${VALIDATION_CONTAINER}" psql -U postgres -d sentinelx_trust_ai_validation < "${BACKUP_FILE}" > /dev/null 2>> "${LOG_FILE}"; then
    echo "❌ ERROR: Restore check failed!" | tee -a "${LOG_FILE}"
    exit 1
fi
echo "✅ SUCCESS: Restore complete." | tee -a "${LOG_FILE}"

# Step 4: Run database schema sanity check
echo "[4/4] Running schema queries validation..." | tee -a "${LOG_FILE}"
TABLE_COUNT=$(docker exec "${VALIDATION_CONTAINER}" psql -U postgres -d sentinelx_trust_ai_validation -t -A -c "
    SELECT count(*) FROM information_schema.tables WHERE table_schema = 'public';
")

if [ "$TABLE_COUNT" -eq 0 ]; then
    echo "❌ ERROR: Restored database contains zero public tables!" | tee -a "${LOG_FILE}"
    exit 1
fi

echo "✅ SUCCESS: Schema verified! Found ${TABLE_COUNT} public tables." | tee -a "${LOG_FILE}"
echo "======================================================================" | tee -a "${LOG_FILE}"
echo "Backup & Restore Integrity Verification: PASSED 🎉" | tee -a "${LOG_FILE}"
echo "======================================================================" | tee -a "${LOG_FILE}"
