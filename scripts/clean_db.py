import sqlite3
from pathlib import Path

def clean_database():
    db_path = Path(__file__).resolve().parents[1] / "data" / "ierl_equity.sqlite3"
    print(f"Connecting to database at: {db_path}")
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    # Check tables
    cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [r[0] for r in cur.fetchall()]
    print("Found tables:", tables)
    
    if "market_cache" in tables:
        dummy_symbols = ('TEST.NS', 'GOOD.NS', 'ALCOHOLIC.NS', 'BOUNDARY.NS')
        cur.execute("DELETE FROM market_cache WHERE symbol IN (?, ?, ?, ?)", dummy_symbols)
        deleted_count = cur.rowcount
        conn.commit()
        
        cur.execute("SELECT COUNT(*) FROM market_cache")
        total_count = cur.fetchone()[0]
        print(f"Purged {deleted_count} dummy test rows. Remaining valid rows in market_cache: {total_count}")
    if "companies" in tables:
        cur.execute("DELETE FROM companies WHERE symbol LIKE 'NF500_%'")
        del_comp = cur.rowcount
        cur.execute("DELETE FROM financial_observations WHERE symbol LIKE 'NF500_%'")
        cur.execute("DELETE FROM business_events WHERE symbol LIKE 'NF500_%'")
        cur.execute("DELETE FROM market_daily_snapshots WHERE symbol LIKE 'NF500_%'")
        conn.commit()
        cur.execute("SELECT COUNT(*) FROM companies")
        total_comp = cur.fetchone()[0]
        print(f"Purged {del_comp} fake NF500_ placeholder companies. Remaining clean companies: {total_comp}")

    conn.close()

if __name__ == '__main__':
    clean_database()
