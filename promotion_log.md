# Deployment Pipeline Promotion Log
## Project: City of Cape Town - Tender Awards Dashboard
## Assessment 6 - Capstone: Ingest to Insight
## Student: Crystal Engelbrecht

---

## ENVIRONMENT OVERVIEW

| Environment | File | Data Source | Purpose |
|-------------|------|-------------|---------|
| Development | powerbi/01_Development.pbix | data/dev/mart_tender_awards_dev.csv | Experimental work, draft visuals, raw data |
| Test | powerbi/02_Test.pbix | data/test/mart_tender_awards_test.csv | Validated data, Power Query checks, verified calculations |
| Production | powerbi/03_Production.pbix | data/prod/mart_tender_awards_prod.csv | Final polished report, production-ready |

---

## PROMOTION 1: Development → Test
**Date:** 2026-05-24
**Promoted by:** Crystal Engelbrecht

### Changes implemented:
- Updated data source path from dev folder to test folder
- Added Power Query validation checks:
  - RowCountCheck - PASS (23 rows above minimum threshold of 20)
  - NullDateCheck - PASS (0 null decision_dates found)
  - FinancialYearCheck - PASS (all rows show 2025-2026)
- Verified all 4 DAX measures calculate correctly (Total Tenders, Active Contracts, Approved Decisions, In Appeals)
- Confirmed star schema relationships correct in Model view (5 relationships)
- Applied Executive colour theme (accessible, avoids red/green combinations)
- Added alt text to all visuals on all 3 pages
- Set tab order on all 3 pages

### Evidence:
- screenshots/pipeline_02_TEST_datasource.png
- screenshots/pipeline_02_TEST_validation1.png
- screenshots/pipeline_02_TEST_validation2.png
- screenshots/pipeline_02_TEST_modelview.png
- screenshots/pipeline_02_TEST_report.png

### Known issues documented (not blockers):
- award_value NULL for most rows - expected, documented in Data Quality Report
- 2 rows have NULL award_type_id - minor mismatch in award_reason text

### Decision: APPROVED TO PROMOTE TO PRODUCTION ✅

---

## PROMOTION 2: Test → Production
**Date:** 2026-05-24
**Promoted by:** Crystal Engelbrecht

### Changes implemented:
- Updated data source path from test folder to prod folder
- Confirmed all 3 Power Query validation checks PASS in Test
- All 3 report pages display correctly (Executive Summary, Department Analysis, Contract Pipeline)
- Star schema model view confirmed with all 5 relationships active
- Accessibility checklist fully completed

### Pre-promotion checklist:
- [x] All Power Query validation checks PASS in Test
- [x] All 3 report pages display correctly
- [x] Star schema Model view confirmed
- [x] Accessibility checklist completed (alt text, tab order, data labels, titles, colour theme)
- [x] No broken relationships in Model view
- [x] Data source updated to prod path

### Evidence:
- screenshots/pipeline_03_PROD_datasource.png
- screenshots/pipeline_03_PROD_modelview.png
- screenshots/pipeline_03_PROD_report.png

### Decision: PROMOTED TO PRODUCTION ✅

---

## ROLLBACK SCENARIO
**Date:** 2026-05-24
**Incident:** Production file accidentally pointed to dev data source instead of prod

### What happened:
During testing of the rollback procedure, 03_Production.pbix was temporarily pointed to the dev data source (data/dev/mart_tender_awards_dev.csv) instead of the prod data source. This simulates a real-world scenario where a deployment error sends the wrong data to Production.

### Impact:
- Production report was showing data from the development environment
- Unvalidated development data was being displayed to end users
- Risk of presenting incorrect information

### Rollback steps taken:
1. Identified wrong data source in 03_Production.pbix via Data Source Settings
2. Took screenshot of broken state (rollback_01_broken_prod.png) as evidence
3. Discarded changes — did NOT save the broken version
4. Re-opened 03_Production.pbix — confirmed it reverted to correct prod path
5. Took screenshot of restored correct state (rollback_02_restored_prod.png)

### Evidence:
- screenshots/rollback_01_broken_prod.png — shows wrong dev path
- screenshots/rollback_02_restored_prod.png — shows correct prod path restored

### Git commit messages used:
- [PROD] ROLLBACK - Fixed wrong data source path pointing to dev instead of prod
- [PROD] Re-promoted after rollback fix

### Lessons learned:
- Always verify data source path after promoting between environments
- Take screenshots before and after any data source change
- The Discard Changes button in Power BI is a critical rollback safety net

### Status: RESOLVED ✅ Production confirmed pointing to correct prod data source

---

## GIT COMMIT HISTORY

| Commit message | What was done |
|----------------|---------------|
| [DEV] Initial build | First version of report built in 01_Development.pbix |
| [DEV] Add star schema model view | Set up 5 relationships in Model view |
| [DEV] Add measures and accessibility | Created DAX measures, added alt text, titles, data labels |
| [TEST] Promoted from Dev with validations | Copied to 02_Test.pbix, added Power Query validation checks |
| [TEST] Validation checks confirmed PASS | All 3 checks passing, ready for production |
| [PROD] Promoted from Test - production ready | Copied to 03_Production.pbix, updated to prod data source |
| [PROD] ROLLBACK - Fixed wrong data source path | Rolled back and corrected data source error |
| [PROD] Re-promoted after rollback fix | Final production version confirmed correct |
| [MONITOR] Updated monitoring.py to track all 3 environments | Email alerts configured, .env security added |
| Final submission - all environments complete | All files committed for submission |
