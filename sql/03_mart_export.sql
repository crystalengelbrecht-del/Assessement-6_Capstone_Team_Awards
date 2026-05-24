-- ════════════════════════════════════════════════════════════════
-- 03_mart_export.sql
-- ════════════════════════════════════════════════════════════════
USE capstone_tenders;

SELECT
    f.tender_id, f.tts_reference, f.description,
    COALESCE(v.vendor_name, 'Unspecified / Panel') AS vendor,
    d.department_name, d.director_name,
    s.status_label AS status,
    y.financial_year, f.decision_date,
    f.award_value, f.budget_value,
    f.decision_code,
    a.award_reason, a.award_category, a.award_description
FROM fact_tender_awards f
JOIN dim_department     d ON f.department_id  = d.department_id
JOIN dim_status         s ON f.status_id      = s.status_id
JOIN dim_financial_year y ON f.year_id        = y.year_id
LEFT JOIN dim_vendor    v ON f.vendor_id      = v.vendor_id
LEFT JOIN dim_award_type a ON f.award_type_id = a.award_type_id;
