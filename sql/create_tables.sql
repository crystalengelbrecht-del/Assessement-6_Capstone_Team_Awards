-- ════════════════════════════════════════════════════════════════
-- Assessment 6 - City of Cape Town Tender Awards
-- ════════════════════════════════════════════════════════════════

-- Step 1: Create and select the database
CREATE DATABASE IF NOT EXISTS capstone_tenders;
USE capstone_tenders;

-- STAGING TABLE: Holds cleaned raw data. 
CREATE TABLE IF NOT EXISTS stg_tender_awards (
    stg_id            INT AUTO_INCREMENT PRIMARY KEY,
    raw_id            INT,
    tts_reference     VARCHAR(50),
    description       TEXT,
    vendor            TEXT,
    decision_date     DATE,
    award_value       DECIMAL(15,2),
    budget_value      DECIMAL(15,2),
    bbbee_level       INT,
    implementing_director   VARCHAR(200),
    implementing_department VARCHAR(200),
    status            VARCHAR(100),
    financial_year    VARCHAR(20),
    award_reason      VARCHAR(200),
    decision_code     VARCHAR(50),
    contract_start    DATE,
    contract_end      DATE,
    s33_award         TINYINT(1),
    loaded_at         DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- DIMENSION: Department
CREATE TABLE IF NOT EXISTS dim_department (
    department_id   INT AUTO_INCREMENT PRIMARY KEY,
    department_name VARCHAR(200) NOT NULL UNIQUE,
    director_name   VARCHAR(200)
);

-- DIMENSION: Status
CREATE TABLE IF NOT EXISTS dim_status (
    status_id     INT AUTO_INCREMENT PRIMARY KEY,
    status_code   VARCHAR(50) NOT NULL UNIQUE,
    status_label  VARCHAR(100)
);

-- DIMENSION: Financial Year
CREATE TABLE IF NOT EXISTS dim_financial_year (
    year_id        INT AUTO_INCREMENT PRIMARY KEY,
    financial_year VARCHAR(20) NOT NULL UNIQUE
);

-- DIMENSION: Vendor
CREATE TABLE IF NOT EXISTS dim_vendor (
    vendor_id   INT AUTO_INCREMENT PRIMARY KEY,
    vendor_name TEXT NOT NULL
);

-- FACT TABLE: 
-- One row per BAC tender decision (the centre of the star schema)
CREATE TABLE IF NOT EXISTS fact_tender_awards (
    fact_id         INT AUTO_INCREMENT PRIMARY KEY,
    tender_id       INT NOT NULL,
    tts_reference   VARCHAR(50),
    description     TEXT,
    decision_date   DATE,
    award_value     DECIMAL(15,2),
    budget_value    DECIMAL(15,2),
    s33_award       TINYINT(1),
    decision_code   VARCHAR(50),
    award_reason    VARCHAR(200),
    department_id   INT,
    status_id       INT,
    year_id         INT,
    vendor_id       INT,
    loaded_at       DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (department_id) REFERENCES dim_department(department_id),
    FOREIGN KEY (status_id)     REFERENCES dim_status(status_id),
    FOREIGN KEY (year_id)       REFERENCES dim_financial_year(year_id),
    FOREIGN KEY (vendor_id)     REFERENCES dim_vendor(vendor_id)
);

-- Confirms all tables were created
SHOW TABLES;