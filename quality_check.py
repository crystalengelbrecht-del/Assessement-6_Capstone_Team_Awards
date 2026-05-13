# ════════════════════════════════════════════════════════════════
# quality_check.py - Data quality checks against MySQL
# ════════════════════════════════════════════════════════════════
import mysql.connector, os
from datetime import datetime

# ── CONFIG: UPDATE YOUR MYSQL PASSWORD HERE ──────────────────────
DB  = dict(host="localhost", user="root",
           password="#Blessed2108", database="capstone_tenders")

# ── FOLDER PATH (matching your actual folder name) ────────────────
OUT = "quality_checks/quality_report.txt"
os.makedirs("quality_checks", exist_ok=True)

conn = mysql.connector.connect(**DB)
cur  = conn.cursor()

def q(sql):
    cur.execute(sql)
    return cur.fetchall()

r = []
r.append("=" * 58)
r.append("  DATA QUALITY REPORT - City of Cape Town Tender Awards")
r.append(f"  Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
r.append("=" * 58)

# Row counts
r.append("\n── ROW COUNTS ──────────────────────────────────────────")
r.append(f"  Staging rows:              {q('SELECT COUNT(*) FROM stg_tender_awards')[0][0]}")
r.append(f"  Fact table rows:           {q('SELECT COUNT(*) FROM fact_tender_awards')[0][0]}")
r.append(f"  dim_department entries:    {q('SELECT COUNT(*) FROM dim_department')[0][0]}")
r.append(f"  dim_status entries:        {q('SELECT COUNT(*) FROM dim_status')[0][0]}")
r.append(f"  dim_financial_year entries:{q('SELECT COUNT(*) FROM dim_financial_year')[0][0]}")
r.append(f"  dim_vendor entries:        {q('SELECT COUNT(*) FROM dim_vendor')[0][0]}")

# Null checks
r.append("\n── NULL CHECKS (key fact table columns) ────────────────")
checks = [
    ("decision_date missing",  "SELECT COUNT(*) FROM fact_tender_awards WHERE decision_date IS NULL"),
    ("department_id missing",  "SELECT COUNT(*) FROM fact_tender_awards WHERE department_id IS NULL"),
    ("status_id missing",      "SELECT COUNT(*) FROM fact_tender_awards WHERE status_id IS NULL"),
    ("year_id missing",        "SELECT COUNT(*) FROM fact_tender_awards WHERE year_id IS NULL"),
    ("award_value missing",    "SELECT COUNT(*) FROM fact_tender_awards WHERE award_value IS NULL"),
    ("budget_value missing",   "SELECT COUNT(*) FROM fact_tender_awards WHERE budget_value IS NULL"),
]
for label, sql in checks:
    count = q(sql)[0][0]
    flag  = "OK" if count == 0 else f"NOTE: {count} rows null"
    r.append(f"  {label:<30}  {flag}")

# Duplicate check
r.append("\n── DUPLICATE CHECK ─────────────────────────────────────")
dupes = q("SELECT tender_id, COUNT(*) c FROM fact_tender_awards GROUP BY tender_id HAVING c > 1")
if dupes:
    r.append(f"  {len(dupes)} tender_id(s) appear more than once")
    r.append("  NOTE: Valid — same tender can go to multiple BAC sessions")
else:
    r.append("  No duplicate tender_ids found  OK")

# Status breakdown
r.append("\n── STATUS BREAKDOWN ────────────────────────────────────")
for row in q("""SELECT s.status_label, COUNT(*) c
                FROM fact_tender_awards f
                JOIN dim_status s ON f.status_id=s.status_id
                GROUP BY s.status_label ORDER BY c DESC"""):
    r.append(f"  {row[0]:<35}  {row[1]}")

# Department breakdown
r.append("\n── TENDERS BY DEPARTMENT ───────────────────────────────")
for row in q("""SELECT d.department_name, COUNT(*) c
                FROM fact_tender_awards f
                JOIN dim_department d ON f.department_id=d.department_id
                GROUP BY d.department_name ORDER BY c DESC"""):
    r.append(f"  {row[0][:52]:<52}  {row[1]}")

# Known limitations
r.append("\n── KNOWN DATA LIMITATIONS (not errors) ─────────────────")
r.append("  award_value: NULL for most rows")
r.append("  Reason: BAC register records decisions in progress;")
r.append("  SAP only receives final values after contract signature.")
r.append("  bbbee_level: 0% populated — not in Open Data export.")
r.append("  Mitigation: documented in postmortem. Phase 2 = SAP join.")

report = "\n".join(r)
print(report)
with open(OUT, "w", encoding="utf-8") as f:
    f.write(report)
print(f"\nQuality report saved to: {OUT}")

cur.close()
conn.close()
