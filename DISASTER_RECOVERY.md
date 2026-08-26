# Equity Lab OS — Disaster Recovery & Backup Manual

## 1️⃣ Emergency Database Restore Procedure

In the event of database corruption or unrecoverable instance failure:

### Automated SQLite Backup & Restore
```bash
# Execute dry-run backup verification
python scripts/backup_and_restore_db.py --action backup

# Restore database from latest verified snapshot
python scripts/backup_and_restore_db.py --action restore --file data/backups/equity_lab_latest.sqlite3
```

### Render PostgreSQL Failover
1. Navigate to the Render Dashboard -> PostgreSQL Instance.
2. Select **Restores** -> Point-in-time Restore (PITR) to restore database instance state.
3. Update `DATABASE_URL` in environment variables if endpoint URL changes.
4. Run preflight gate to verify database readiness:
   ```bash
   python scripts/preflight_check.py
   ```

---

## 2️⃣ Verification & System Health Gate

After executing any disaster recovery action:
```bash
python scripts/build_and_test.py
```
Ensure all 418/418 unit and integration tests pass before restoring traffic.
