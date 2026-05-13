# ════════════════════════════════════════════════════════════════
# monitor.py - Run after every data refresh for alert proof
# ════════════════════════════════════════════════════════════════
import mysql.connector, os
from datetime import datetime

# ── CONFIG: UPDATE YOUR MYSQL PASSWORD HERE ──────────────────────
DB  = dict(host="localhost", user="root",
           password="#Blessed2108", database="capstone_tenders")

# ── FOLDER PATH (matching your actual folder name) ────────────────
LOG = "quality_checks/monitor_log.txt"
os.makedirs("quality_checks", exist_ok=True)

EXPECTED_MIN_ROWS = 20

conn = mysql.connector.connect(**DB)
cur  = conn.cursor()

cur.execute("SELECT COUNT(*) FROM fact_tender_awards")
row_count = cur.fetchone()[0]

cur.execute("SELECT MAX(loaded_at) FROM fact_tender_awards")
last_load = cur.fetchone()[0]

cur.close()
conn.close()

row_status = (
    "OK" if row_count >= EXPECTED_MIN_ROWS
    else f"ALERT: only {row_count} rows — below threshold of {EXPECTED_MIN_ROWS}!"
)

if last_load:
    days_old     = (datetime.now() - last_load).days
    fresh_status = (
        "OK" if days_old <= 7
        else f"ALERT: data is {days_old} days old — refresh needed!"
    )
else:
    fresh_status = "ALERT: no load timestamp found — has ingest.py run?"

entry = (
    f"{datetime.now().strftime('%Y-%m-%d %H:%M')} | "
    f"Rows: {row_count} | Row check: {row_status} | Freshness: {fresh_status}"
)

print(entry)
with open(LOG, "a", encoding="utf-8") as f:
    f.write(entry + "\n")
print(f"Monitor log updated: {LOG}")
