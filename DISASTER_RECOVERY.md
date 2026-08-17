# IERL OS v0.3.4-MASTER — Disaster Recovery Runbook

This runbook documents operational disaster recovery procedures for the Hostinger Business (Frontend) + Hostinger VPS (FastAPI Backend) deployment.

---

## 1. System Failover & Incident Taxonomy

| Incident Type | Severity | Primary Mitigation | Target Recovery Time (RTO) |
| :--- | :--- | :--- | :--- |
| **Database Corruption / Lock** | CRITICAL | Run `scripts/backup_restore_verify.py` & restore latest `.sqlite` backup | < 15 minutes |
| **API Provider Outage (yfinance / Market Feed)** | MAJOR | Automatic fallback to cached quotes / secondary provider in `market_data` service | < 1 minute (Automatic) |
| **LLM Provider API Key Expiration** | MINOR | Update `API_KEYS_CONFIG.env` or environment panel & restart FastAPI worker | < 5 minutes |
| **Hostinger VPS Worker Outage** | CRITICAL | SSH restart `gunicorn`/`uvicorn` systemd service or trigger emergency fallback container | < 10 minutes |

---

## 2. Emergency Backup & Restore Procedure

### Manual Database Restoration
To restore the SQLite database from a timestamped backup:
```bash
# 1. Stop FastAPI backend service
systemctl stop ierl-backend

# 2. Verify backup integrity using script
python scripts/backup_restore_verify.py

# 3. Restore latest clean backup
cp backups/ierl_backup_YYYYMMDD_HHMMSS.sqlite app/data/ierl_datastore.sqlite

# 4. Verify integrity
sqlite3 app/data/ierl_datastore.sqlite "PRAGMA integrity_check;"

# 5. Restart backend service
systemctl start ierl-backend
```

---

## 3. Rollback Procedure

To roll back a production deployment to a known clean state:
```bash
# 1. Checkout stable Git release tag
git checkout tags/v0.3.4-MASTER

# 2. Run preflight check
python scripts/preflight_check.py

# 3. Re-run complete test suite
python -m pytest app/tests -v

# 4. Restart services
systemctl restart ierl-backend
```
