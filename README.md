# Assessment 6 - End-to-End Capstone: Ingest to Insight

## Dataset
**City of Cape Town - Tender Awards**  
Contracts awarded to contractors with a value of more than R200 000.  
Source: City of Cape Town Open Data Portal (Corporate GIS)

## Tools
| Tool | Purpose |
|------|---------|
| VSCode | Writing and running Python scripts |
| MySQL Workbench | Staging and mart database (star schema) |
| GitHub Desktop | Version control and repository management |
| Power BI Desktop | Reporting and visualisation (free - no licence required) |

## Folder Structure
```
Assessement 6_Capstone_Team_Awards/
├── raw_data/                 ← Original CSV (never edited)
├── 02_staging/               ← Python watermark file (last_load.txt)
├── 03_mart/                  ← All dimension and fact CSVs for Power BI
│   ├── fact_tender_awards.csv
│   ├── dim_department.csv
│   ├── dim_status.csv
│   ├── dim_financial_year.csv
│   ├── dim_vendor.csv
│   ├── dim_award_type.csv
│   └── mart_tender_awards.csv
├── data/
│   ├── dev/                  ← mart_tender_awards_dev.csv
│   ├── test/                 ← mart_tender_awards_test.csv
│   └── prod/                 ← mart_tender_awards_prod.csv
├── quality_checks/           ← quality_report.txt + monitor_log.txt
├── powerbi/
│   ├── 01_Development.pbix   ← Development environment
│   ├── 02_Test.pbix          ← Test environment (Power Query validation checks)
│   └── 03_Production.pbix    ← Production environment (final polished report)
├── sql/                      ← All MySQL scripts
├── screenshots/              ← All pipeline and evidence screenshots
├── docs/                     ← Data Quality Report + Prompt Reflection Log
├── ingest.py                 ← Incremental ingest script
├── quality_check.py          ← Data quality checks against MySQL
├── monitoring.py             ← Environment monitor + email alert script
├── promotion_log.md          ← DEV→TEST→PROD promotion log + rollback documentation
├── .gitignore                ← Prevents .env from uploading to GitHub
└── README.md                 ← This file
```

## How to Run (in order)

### Step 1: Set up MySQL
Open MySQL Workbench → run `sql/create_tables.sql`

### Step 2: Load data incrementally
```bash
python ingest.py
```

### Step 3: Run quality checks
```bash
python quality_check.py
```

### Step 4: Run environment monitor
```bash
python monitoring.py
```
Sends email alert if any check fails. Credentials stored in `.env` (not committed to GitHub).

### Step 5: Export mart from MySQL
Run `sql/mart_export.sql` in MySQL Workbench → export results as CSV to `03_mart/`

### Step 6: Open Power BI
Load CSVs from `03_mart/` into Power BI Desktop. No sign-in required.

## Star Schema (MySQL - capstone_tenders database)
| Table | Type | Description |
|-------|------|-------------|
| fact_tender_awards | Fact | One row per BAC tender decision — the grain |
| dim_department | Dimension | City department + director name (16 departments) |
| dim_status | Dimension | 6 tender pipeline statuses |
| dim_financial_year | Dimension | Financial year lookup |
| dim_vendor | Dimension | Vendor / contractor names (21 vendors) |
| dim_award_type | Dimension | Award decision type: Competitive, Amendment, Cancellation etc. |

## Deployment Pipeline (Simulated)
| Environment | File | Data Source |
|-------------|------|-------------|
| Development | powerbi/01_Development.pbix | data/dev/mart_tender_awards_dev.csv |
| Test | powerbi/02_Test.pbix | data/test/mart_tender_awards_test.csv |
| Production | powerbi/03_Production.pbix | data/prod/mart_tender_awards_prod.csv |

See `promotion_log.md` for full promotion and rollback documentation.

## Monitoring and Alerts
- Script: `monitoring.py`
- Checks: all 3 .pbix files exist, MySQL row count >= 20, data freshness <= 7 days, null checks on key columns
- Alert: sends email via Gmail SMTP when any check fails
- Log: `quality_checks/monitor_log.txt`
- Credentials: stored in `.env` (excluded from GitHub via `.gitignore`)

## Data Quality Notes
See `quality_checks/quality_report.txt`  
Full report: `docs/Data_Quality_Report.docx`

## Known Limitation
Award values are NULL for most rows. This is expected - the source dataset is the BAC decisions register, not the contracts register. Fixed values only appear in SAP after contract signature. See postmortem in Data Quality Report.
