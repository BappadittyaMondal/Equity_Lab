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
    else:
        print("market_cache table not present.")
    
    conn.close()

if __name__ == '__main__':
    clean_database()
