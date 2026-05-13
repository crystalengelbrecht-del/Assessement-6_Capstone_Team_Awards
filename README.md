# Assessment 6 — End-to-End Capstone: Ingest to Insight

## Dataset
**City of Cape Town — Tender Awards**  
Contracts awarded to contractors with a value of more than R200 000.  
Source: City of Cape Town Open Data Portal (Corporate GIS)

## Tools
| Tool | Purpose |
|------|---------|
| VSCode | Writing and running Python scripts |
| MySQL Workbench | Staging and mart database (star schema) |
| GitHub | Repository and version control |
| Power BI Desktop | Reporting and visualisation (free app) |

## Folder Structure
```
capstone_tender_awards/
├── 01_raw_data/          ← Original CSV (never edited)
├── 02_staging/           ← Python writes watermark file here
├── 03_mart/              ← mart_tender_awards.csv for Power BI
├── 04_quality_checks/    ← quality_report.txt + monitor_log.txt
├── 05_powerbi/           ← .pbix files (DEV / TEST / PROD)
├── 06_sql/               ← All MySQL scripts
├── 07_screenshots/       ← All pipeline screenshots
├── 08_documentation/     ← Word docs: Step-by-Step Guide, Data Quality Report, Prompt Reflection Log
├── 02_ingest.py          ← Main ingest script (incremental)
├── 03_quality_check.py   ← Data quality checks
├── 04_monitor.py         ← Monitoring and alert script
└── README.md             ← This file
```

## How to Run (in order)

### Step 1: Set up MySQL
Open MySQL Workbench → run `06_sql/01_create_tables.sql`

### Step 2: Load data
```bash
python 02_ingest.py
```

### Step 3: Quality check
```bash
python 03_quality_check.py
```

### Step 4: Monitor
```bash
python 04_monitor.py
```

### Step 5: Export mart
Run `06_sql/03_mart_export.sql` in MySQL Workbench → export results as CSV → save to `03_mart/mart_tender_awards.csv`

### Step 6: Open Power BI
Load `03_mart/mart_tender_awards.csv` into Power BI Desktop (free — no sign-in required)

## Star Schema
- **Fact table:** `fact_tender_awards` — one row per BAC tender decision
- **dim_department** — City department + director name
- **dim_status** — 6 tender statuses (Active Contract, Preferred Bidder, etc.)
- **dim_financial_year** — Financial year lookup
- **dim_vendor** — Vendor / contractor names

## Data Quality Notes
See `04_quality_checks/quality_report.txt`  
Full report: `08_documentation/02_Data_Quality_Report.docx`

## Known Limitation
Award values are NULL for most rows. This is expected — the source dataset is the BAC decisions register, not the contracts register. Fixed values only appear in SAP after contract signature. See postmortem in Data Quality Report.
