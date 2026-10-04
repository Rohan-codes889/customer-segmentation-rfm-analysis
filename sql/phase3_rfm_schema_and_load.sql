-- Phase 3, Step 1: MySQL schema and CSV load for RFM customer analytics.
-- Run against a new/empty MySQL database. This script intentionally contains
-- no analytical queries.

CREATE TABLE rfm_customers (
    customer_id INT UNSIGNED NOT NULL,
    recency_days SMALLINT UNSIGNED NOT NULL,
    frequency_invoices SMALLINT UNSIGNED NOT NULL,
    monetary_value DECIMAL(15, 2) NOT NULL,
    r_score TINYINT UNSIGNED NOT NULL,
    f_score TINYINT UNSIGNED NOT NULL,
    m_score TINYINT UNSIGNED NOT NULL,
    segment VARCHAR(40) NOT NULL,
    PRIMARY KEY (customer_id),
    CONSTRAINT chk_r_score CHECK (r_score BETWEEN 1 AND 5),
    CONSTRAINT chk_f_score CHECK (f_score BETWEEN 1 AND 5),
    CONSTRAINT chk_m_score CHECK (m_score BETWEEN 1 AND 5)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE retail_transactions (
    transaction_id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    invoice VARCHAR(20) NOT NULL,
    stock_code VARCHAR(30) NOT NULL,
    description TEXT NULL,
    quantity INT NOT NULL,
    invoice_date DATETIME NOT NULL,
    unit_price DECIMAL(12, 4) NOT NULL,
    customer_id INT UNSIGNED NOT NULL,
    country VARCHAR(60) NOT NULL,
    PRIMARY KEY (transaction_id),
    INDEX idx_transactions_customer (customer_id),
    INDEX idx_transactions_invoice_date (invoice_date),
    CONSTRAINT fk_transactions_customer
        FOREIGN KEY (customer_id) REFERENCES rfm_customers(customer_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- MySQL client prerequisite: enable LOCAL loading for this session/client.
-- Example connection: mysql --local-infile=1 -u <user> -p <database>
-- If your server disables it, a privileged administrator may need:
-- SET GLOBAL local_infile = ON;

LOAD DATA LOCAL INFILE 'C:/Users/rohan/Downloads/RFM project/rfm_segmented.csv'
INTO TABLE rfm_customers
CHARACTER SET utf8mb4
FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"' ESCAPED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 LINES
(@customer_id, @recency_days, @frequency_invoices, @monetary_value,
 @r_score, @f_score, @m_score, @segment)
SET customer_id = CAST(CAST(@customer_id AS DECIMAL(10,1)) AS UNSIGNED),
    recency_days = CAST(@recency_days AS UNSIGNED),
    frequency_invoices = CAST(@frequency_invoices AS UNSIGNED),
    monetary_value = CAST(@monetary_value AS DECIMAL(15,2)),
    r_score = CAST(@r_score AS UNSIGNED),
    f_score = CAST(@f_score AS UNSIGNED),
    m_score = CAST(@m_score AS UNSIGNED),
    segment = TRIM(@segment);

LOAD DATA LOCAL INFILE 'C:/Users/rohan/Downloads/RFM project/online_retail_II_cleaned_rfm.csv'
INTO TABLE retail_transactions
CHARACTER SET utf8mb4
FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"' ESCAPED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 LINES
(@invoice, @stock_code, @description, @quantity, @invoice_date,
 @unit_price, @customer_id, @country)
SET invoice = TRIM(@invoice),
    stock_code = TRIM(@stock_code),
    description = NULLIF(TRIM(@description), ''),
    quantity = CAST(@quantity AS SIGNED),
    invoice_date = STR_TO_DATE(@invoice_date, '%Y-%m-%d %H:%i:%s'),
    unit_price = CAST(@unit_price AS DECIMAL(12,4)),
    customer_id = CAST(CAST(@customer_id AS DECIMAL(10,1)) AS UNSIGNED),
    country = TRIM(@country);

-- Load verification: both counts must match the verified CSV row counts.
SELECT 'rfm_customers' AS table_name, COUNT(*) AS actual_rows, 5878 AS expected_rows
FROM rfm_customers
UNION ALL
SELECT 'retail_transactions', COUNT(*), 779425
FROM retail_transactions;

-- Integrity checks: both values must be zero.
SELECT
    (SELECT COUNT(*) FROM retail_transactions t
     LEFT JOIN rfm_customers c ON t.customer_id = c.customer_id
     WHERE c.customer_id IS NULL) AS transactions_without_customer,
    (SELECT COUNT(*) FROM retail_transactions
     WHERE invoice_date IS NULL) AS transactions_with_unparsed_date;
