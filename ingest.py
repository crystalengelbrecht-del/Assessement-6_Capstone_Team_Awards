# ════════════════════════════════════════════════════════════════
# ingest.py  - Load Tender Awards CSV into MySQL
# ════════════════════════════════════════════════════════════════
import pandas as pd
import mysql.connector
from datetime import datetime
import math, os

# ── CONFIG: UPDATE YOUR MYSQL PASSWORD HERE ──────────────────────
DB = dict(
    host     = "localhost",
    user     = "root",
    password = "#Blessed2108",   # <-- change this to your MySQL password
    database = "capstone_tenders"
)

RAW       = "raw_data/Tender_Awards.csv"
WATERMARK = "02_staging/last_load.txt"

os.makedirs("02_staging", exist_ok=True)
os.makedirs("03_mart",    exist_ok=True)

# ── HELPER: safely return None for NaN/null values ───────────────
def safe(v):
    if v is None:
        return None
    try:
        if math.isnan(float(v)):
            return None
    except (TypeError, ValueError):
        pass
    return v

# ── HELPER: clean South African Rand currency strings ────────────
# SA Rand uses SPACE as thousands separator, e.g. "R13 466 765.00"
# We must remove "R", all spaces, and any commas before converting
def clean_zar(series):
    return pd.to_numeric(
        series.astype(str)
              .str.replace('R', '', regex=False)
              .str.replace(' ', '', regex=False)
              .str.replace(',', '', regex=False)
              .str.strip(),
        errors='coerce'
    )

# ── 1. READ & CLEAN ──────────────────────────────────────────────
print("Reading CSV...")
df = pd.read_csv(RAW, encoding="latin-1")
print(f"  Raw rows loaded: {len(df)}")

df = df.rename(columns={
    "ID":                               "raw_id",
    "TTS Reference":                    "tts_reference",
    "Description":                      "description",
    "Vendor":                           "vendor",
    "Date of decision":                 "decision_date",
    "Value of Decision (Fixed)":        "award_value",
    "Budget Value (Rates based)":       "budget_value",
    "BBBEE Level":                      "bbbee_level",
    "TTS:Implementing Director":        "implementing_director",
    "TTS:Implementing Department":      "implementing_department",
    "TTS:Status":                       "status",
    "Financial Year":                   "financial_year",
    "Reason":                           "award_reason",
    "Decision Code":                    "decision_code",
    "TTS:Commencement Date of Contract":"contract_start",
    "TTS:Expiry Date of Contract":      "contract_end",
    "S33 Award":                        "s33_award",
})

cols = [
    "raw_id", "tts_reference", "description", "vendor", "decision_date",
    "award_value", "budget_value", "bbbee_level", "implementing_director",
    "implementing_department", "status", "financial_year", "award_reason",
    "decision_code", "contract_start", "contract_end", "s33_award"
]
df = df[[c for c in cols if c in df.columns]]

# Fix bad financial year (Excel date serialisation error: 0 = 1 Jan 1900)
df["financial_year"] = df["financial_year"].replace("1899-1900", None)

# Fill blank vendors
df["vendor"] = df["vendor"].fillna("Unspecified / Panel")

# Clean monetary columns - SA Rand uses SPACE as thousands separator
df["award_value"]  = clean_zar(df["award_value"])
df["budget_value"] = clean_zar(df["budget_value"])

# Parse dates safely (format in CSV is YYYY/MM/DD)
for col in ["decision_date", "contract_start", "contract_end"]:
    if col in df.columns:
        df[col] = pd.to_datetime(df[col], errors="coerce").dt.date

# Convert boolean s33_award to integer (MySQL uses TINYINT)
if "s33_award" in df.columns:
    df["s33_award"] = df["s33_award"].astype(bool).astype(int)

print(f"  Cleaned rows ready: {len(df)}")
print(f"  Award value populated: {df['award_value'].notna().sum()} rows")
print(f"  Budget value populated: {df['budget_value'].notna().sum()} rows")

# ── 2. CONNECT TO MYSQL ───────────────────────────────────────────
print("Connecting to MySQL...")
conn = mysql.connector.connect(**DB)
cur  = conn.cursor()

# ── 3. INCREMENTAL CHECK - only insert rows not already in staging
cur.execute("SELECT raw_id FROM stg_tender_awards")
existing_ids = {row[0] for row in cur.fetchall()}
new_rows = df[~df["raw_id"].isin(existing_ids)]
print(f"  Already in staging:  {len(existing_ids)} rows")
print(f"  New rows to insert:  {len(new_rows)} rows")

# ── 4. LOAD STAGING ──────────────────────────────────────────────
if len(new_rows) > 0:
    insert_stg = """
        INSERT INTO stg_tender_awards
        (raw_id, tts_reference, description, vendor, decision_date,
         award_value, budget_value, bbbee_level, implementing_director,
         implementing_department, status, financial_year, award_reason,
         decision_code, contract_start, contract_end, s33_award)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """
    for _, row in new_rows.iterrows():
        vals = (
            safe(row.get("raw_id")),
            safe(row.get("tts_reference")),
            safe(row.get("description")),
            safe(row.get("vendor")),
            safe(row.get("decision_date")),
            safe(row.get("award_value")),
            safe(row.get("budget_value")),
            safe(row.get("bbbee_level")),
            safe(row.get("implementing_director")),
            safe(row.get("implementing_department")),
            safe(row.get("status")),
            safe(row.get("financial_year")),
            safe(row.get("award_reason")),
            safe(row.get("decision_code")),
            safe(row.get("contract_start")),
            safe(row.get("contract_end")),
            safe(row.get("s33_award")),
        )
        cur.execute(insert_stg, vals)
    conn.commit()
    print(f"  Staging loaded: {len(new_rows)} rows inserted")
else:
    print("  No new rows - staging already up to date")

# Save watermark (records when we last ran the ingest)
with open(WATERMARK, "w") as f:
    f.write(datetime.now().strftime("%Y-%m-%d %H:%M"))

# ── 5. POPULATE DIMENSION TABLES ─────────────────────────────────
print("Populating dimension tables...")

# dim_department - one row per unique department name
cur.execute("SELECT department_name FROM dim_department")
existing_depts = {r[0] for r in cur.fetchall()}
depts = (df[["implementing_department", "implementing_director"]]
         .dropna(subset=["implementing_department"])
         .drop_duplicates(subset=["implementing_department"]))
for _, r in depts.iterrows():
    name = r["implementing_department"]
    if name not in existing_depts:
        cur.execute(
            "INSERT IGNORE INTO dim_department (department_name, director_name) VALUES (%s,%s)",
            (name, safe(r.get("implementing_director")))
        )
conn.commit()

# dim_status - one row per unique status code
cur.execute("SELECT status_code FROM dim_status")
existing_statuses = {r[0] for r in cur.fetchall()}
for s in df["status"].dropna().unique():
    # Strip leading "16. " etc to get clean label
    label = s.split(". ", 1)[-1] if ". " in s else s
    if s not in existing_statuses:
        cur.execute(
            "INSERT IGNORE INTO dim_status (status_code, status_label) VALUES (%s,%s)",
            (s, label)
        )
conn.commit()

# dim_financial_year - one row per year
cur.execute("SELECT financial_year FROM dim_financial_year")
existing_years = {r[0] for r in cur.fetchall()}
for y in df["financial_year"].dropna().unique():
    if y not in existing_years:
        cur.execute("INSERT IGNORE INTO dim_financial_year (financial_year) VALUES (%s)", (y,))
conn.commit()

# dim_vendor - one row per unique vendor string
cur.execute("SELECT vendor_name FROM dim_vendor")
existing_vendors = {r[0] for r in cur.fetchall()}
for v in df["vendor"].dropna().unique():
    if v not in existing_vendors:
        cur.execute("INSERT IGNORE INTO dim_vendor (vendor_name) VALUES (%s)", (v,))
conn.commit()

print("  Dimension tables populated")

# ── 6. POPULATE FACT TABLE ───────────────────────────────────────
print("Populating fact table...")

# Build lookup maps (dim table name → ID)
cur.execute("SELECT department_name, department_id FROM dim_department")
dept_map = {r[0]: r[1] for r in cur.fetchall()}

cur.execute("SELECT status_code, status_id FROM dim_status")
status_map = {r[0]: r[1] for r in cur.fetchall()}

cur.execute("SELECT financial_year, year_id FROM dim_financial_year")
year_map = {r[0]: r[1] for r in cur.fetchall()}

cur.execute("SELECT vendor_name, vendor_id FROM dim_vendor")
vendor_map = {r[0]: r[1] for r in cur.fetchall()}

cur.execute("SELECT tender_id FROM fact_tender_awards")
existing_fact_ids = {r[0] for r in cur.fetchall()}

fact_sql = """
    INSERT INTO fact_tender_awards
    (tender_id, tts_reference, description, decision_date,
     award_value, budget_value, s33_award, decision_code, award_reason,
     department_id, status_id, year_id, vendor_id)
    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
"""

inserted = 0
for _, row in new_rows.iterrows():
    tid = row.get("raw_id")
    if tid not in existing_fact_ids:
        cur.execute(fact_sql, (
            tid,
            safe(row.get("tts_reference")),
            safe(row.get("description")),
            safe(row.get("decision_date")),
            safe(row.get("award_value")),
            safe(row.get("budget_value")),
            safe(row.get("s33_award")),
            safe(row.get("decision_code")),
            safe(row.get("award_reason")),
            dept_map.get(row.get("implementing_department")),
            status_map.get(row.get("status")),
            year_map.get(row.get("financial_year")),
            vendor_map.get(row.get("vendor")),
        ))
        inserted += 1

conn.commit()
cur.close()
conn.close()

print(f"  Fact table: {inserted} new rows inserted")
print()
print("All done!")

