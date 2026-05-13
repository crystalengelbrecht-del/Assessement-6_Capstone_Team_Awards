INSERT INTO fact_tender_awards (
    tender_id, tts_reference, description, decision_date, 
    award_value, budget_value, s33_award, decision_code, 
    award_reason, department_id, status_id, year_id, vendor_id
)
SELECT 
    s.raw_id, s.tts_reference, s.description, s.decision_date,
    s.award_value, s.budget_value, s.s33_award, s.decision_code,
    s.award_reason, d.department_id, st.status_id, y.year_id, v.vendor_id
FROM stg_tender_awards s
LEFT JOIN dim_department d ON s.implementing_department = d.department_name
LEFT JOIN dim_status st ON s.status = st.status_code
LEFT JOIN dim_financial_year y ON s.financial_year = y.financial_year
LEFT JOIN dim_vendor v ON s.vendor = v.vendor_name;