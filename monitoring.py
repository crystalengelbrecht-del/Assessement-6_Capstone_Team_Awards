# ════════════════════════════════════════════════════════════════
# monitoring.py — Monitors all 3 deployment environments
# Tracks: MySQL data health + existence of all 3 .pbix files
# HOW TO RUN: python monitoring.py
# Update your_mysql_password below first!
# ════════════════════════════════════════════════════════════════
import mysql.connector, os, smtplib
from datetime import datetime
from email.mime.text import MIMEText

# ── CONFIG ───────────────────────────────────────────────────────
from dotenv import load_dotenv
load_dotenv()

DB = dict(host="localhost", user="root",
          password=os.getenv("MYSQL_PASSWORD"), database="capstone_tenders")

EMAIL_SENDER   = os.getenv("EMAIL_SENDER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
EMAIL_RECEIVER = os.getenv("EMAIL_RECEIVER")

EXPECTED_MIN_ROWS  = 20
MAX_STALENESS_DAYS = 7

LOG = "quality_checks/monitor_log.txt"
os.makedirs("quality_checks", exist_ok=True)

# ── ENVIRONMENT FILE TRACKING ─────────────────────────────────────
# These are the 3 .pbix files representing your pipeline environments
files_to_monitor = {
    "DEV  (01_Development.pbix)" : "powerbi/01_Development.pbix",
    "TEST (02_Test.pbix)"        : "powerbi/02_Test.pbix",
    "PROD (03_Production.pbix)"  : "powerbi/03_Production.pbix",
}

# ── DATA SOURCE FILES ─────────────────────────────────────────────
data_sources = {
    "DEV  data source" : "data/dev/mart_tender_awards_dev.csv",
    "TEST data source" : "data/test/mart_tender_awards_test.csv",
    "PROD data source" : "data/prod/mart_tender_awards_prod.csv",
}

print("=" * 58)
print("  ENVIRONMENT MONITOR — City of Cape Town Tender Awards")
print(f"  Run at: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
print("=" * 58)

alerts = []
all_ok = True
report_lines = []

# ── CHECK 1: ALL 3 PBIX FILES EXIST ──────────────────────────────
print("\n── ENVIRONMENT FILE CHECK ──────────────────────────────")
report_lines.append("── ENVIRONMENT FILE CHECK ──────────────────────────────")

for env_name, filepath in files_to_monitor.items():
    exists = os.path.exists(filepath)
    status = "OK — file found" if exists else "ALERT — FILE MISSING!"
    flag   = "✅" if exists else "❌"
    line   = f"  {flag} {env_name:<35} {status}"
    print(line)
    report_lines.append(line)
    if not exists:
        alerts.append(f"MISSING FILE: {filepath} not found in powerbi folder")
        all_ok = False

# ── CHECK 2: DATA SOURCE FILES EXIST ─────────────────────────────
print("\n── DATA SOURCE FILE CHECK ──────────────────────────────")
report_lines.append("── DATA SOURCE FILE CHECK ──────────────────────────────")

for src_name, filepath in data_sources.items():
    exists = os.path.exists(filepath)
    status = "OK — file found" if exists else "NOTE — file not found (normal if using mart folder)"
    flag   = "✅" if exists else "⚠️"
    line   = f"  {flag} {src_name:<30} {status}"
    print(line)
    report_lines.append(line)

# ── CHECK 3: MYSQL DATA HEALTH ────────────────────────────────────
print("\n── MYSQL DATA HEALTH CHECK ─────────────────────────────")
report_lines.append("── MYSQL DATA HEALTH CHECK ─────────────────────────────")

try:
    conn = mysql.connector.connect(**DB)
    cur  = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM fact_tender_awards")
    row_count = cur.fetchone()[0]

    cur.execute("SELECT MAX(loaded_at) FROM fact_tender_awards")
    last_load = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM fact_tender_awards WHERE decision_date IS NULL")
    null_dates = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM fact_tender_awards WHERE department_id IS NULL")
    null_depts = cur.fetchone()[0]

    cur.close()
    conn.close()

    # Row count check
    if row_count < EXPECTED_MIN_ROWS:
        row_status = f"ALERT — only {row_count} rows (expected >= {EXPECTED_MIN_ROWS})"
        alerts.append(f"Row count FAILED: {row_count} rows found, expected at least {EXPECTED_MIN_ROWS}")
        all_ok = False
    else:
        row_status = f"OK — {row_count} rows"

    # Freshness check
    if last_load:
        days_old = (datetime.now() - last_load).days
        if days_old > MAX_STALENESS_DAYS:
            fresh_status = f"ALERT — data is {days_old} days old (max allowed: {MAX_STALENESS_DAYS})"
            alerts.append(f"Data freshness FAILED: {days_old} days old")
            all_ok = False
        else:
            fresh_status = f"OK — {days_old} days old"
    else:
        fresh_status = "ALERT — no load timestamp"
        alerts.append("No load timestamp found in fact table")
        all_ok = False

    # Null checks
    null_date_status = "OK" if null_dates == 0 else f"ALERT — {null_dates} rows with null decision_date"
    null_dept_status = "OK" if null_depts == 0 else f"ALERT — {null_depts} rows with null department_id"
    if null_dates > 0:
        alerts.append(f"Null check FAILED: {null_dates} rows have no decision_date")
        all_ok = False
    if null_depts > 0:
        alerts.append(f"Null check FAILED: {null_depts} rows have no department_id")
        all_ok = False

    for line in [
        f"  Fact table rows      : {row_status}",
        f"  Data freshness       : {fresh_status}",
        f"  Null decision_date   : {null_date_status}",
        f"  Null department_id   : {null_dept_status}",
    ]:
        print(line)
        report_lines.append(line)

except Exception as e:
    err = f"  ALERT — Could not connect to MySQL: {e}"
    print(err)
    report_lines.append(err)
    alerts.append(f"MySQL connection FAILED: {e}")
    all_ok = False

# ── OVERALL STATUS ────────────────────────────────────────────────
overall = "ALL CHECKS PASSED ✅" if all_ok else "FAILURES DETECTED ❌"
print(f"\n── OVERALL STATUS: {overall}")
report_lines.append(f"── OVERALL STATUS: {overall}")

if alerts:
    print("\nALERTS:")
    for a in alerts:
        line = f"  >>> {a}"
        print(line)
        report_lines.append(line)

# ── WRITE TO LOG ──────────────────────────────────────────────────
timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
log_entry = f"\n{'='*58}\nRUN: {timestamp} | Status: {overall}\n"
log_entry += "\n".join(report_lines)

with open(LOG, "a", encoding="utf-8") as f:
    f.write(log_entry + "\n")
print(f"\nLog updated: {LOG}")

# ── SEND EMAIL ALERT ──────────────────────────────────────────────
if not all_ok:
    print("\nSending alert email...")
    subject = f"ALERT: Tender Awards Dashboard — Environment Monitor Failure {timestamp}"
    body = f"""
City of Cape Town — Tender Awards Dashboard
Environment Monitor Alert
Generated: {timestamp}
Overall Status: FAILURE

ALERTS DETECTED:
{chr(10).join(f'  • {a}' for a in alerts)}

ENVIRONMENTS CHECKED:
  DEV  → powerbi/01_Development.pbix
  TEST → powerbi/02_Test.pbix
  PROD → powerbi/03_Production.pbix

ACTION REQUIRED:
  1. Check that all 3 .pbix files are in the powerbi folder
  2. Run python ingest.py if data is stale
  3. Run python monitoring.py again to confirm fix

This is an automated alert from the Assessment 6 monitoring script.
    """.strip()

    try:
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From']    = EMAIL_SENDER
        msg['To']      = EMAIL_RECEIVER

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.send_message(msg)
        print(f"Alert email sent to {EMAIL_RECEIVER}")

        with open(LOG, "a", encoding="utf-8") as f:
            f.write(f"  >>> EMAIL ALERT SENT to {EMAIL_RECEIVER} at {timestamp}\n")

    except Exception as e:
        print(f"Email failed: {e}")
        with open(LOG, "a", encoding="utf-8") as f:
            f.write(f"  >>> EMAIL FAILED: {e}\n")
else:
    print("All checks passed — no alert email needed.")
