-- ════════════════════════════════════════════════════════════════
-- verify_star_schema.sql
-- ════════════════════════════════════════════════════════════════
-- Checking that the data is in the staging table
USE capstone_tenders;
SELECT COUNT(*) AS total_staging_rows FROM stg_tender_awards;

-- Checking the dimension tables populated correctly
SELECT * FROM dim_department;
SELECT * FROM dim_status;
SELECT * FROM dim_financial_year;
SELECT * FROM dim_vendor LIMIT 10;

-- Checking the fact table
SELECT
    f.tender_id,
    f.tts_reference,
    d.department_name,
    s.status_label,
    y.financial_year,
    f.decision_date,
    f.award_value
FROM fact_tender_awards f
JOIN dim_department   d ON f.department_id = d.department_id
JOIN dim_status       s ON f.status_id     = s.status_id
JOIN dim_financial_year y ON f.year_id     = y.year_id
LIMIT 10;
