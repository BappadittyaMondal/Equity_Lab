import sqlite3

conn = sqlite3.connect('ierl_equity.sqlite3')
cur = conn.cursor()
cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = [r[0] for r in cur.fetchall()]
print("Tables in ierl_equity.sqlite3:", tables)
conn.close()
