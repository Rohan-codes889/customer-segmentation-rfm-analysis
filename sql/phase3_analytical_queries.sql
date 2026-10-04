-- Phase 3, Step 2: Analytical SQL queries for RFM customer analytics.
-- Run against rfm_project database after phase3_rfm_schema_and_load.sql
-- has been executed and verified (5,878 customers, 779,425 transactions).

-- ==================================================
-- Q1. Revenue and customer count by segment
-- ==================================================
SELECT
    c.segment,
    COUNT(DISTINCT c.customer_id) AS num_customers,
    ROUND(SUM(t.quantity * t.unit_price), 2) AS total_revenue
FROM rfm_customers c
JOIN retail_transactions t ON t.customer_id = c.customer_id
GROUP BY c.segment
ORDER BY total_revenue DESC;

-- ==================================================
-- Q2. Top 10 customers by monetary value (with segment and country)
-- ==================================================
SELECT
    c.customer_id,
    c.monetary_value,
    c.segment,
    t.country
FROM rfm_customers c
JOIN (
    SELECT customer_id, country
    FROM retail_transactions
    GROUP BY customer_id, country
) t ON t.customer_id = c.customer_id
ORDER BY c.monetary_value DESC
LIMIT 10;

-- ==================================================
-- Q3. Monthly revenue trend (full transaction history)
-- ==================================================
SELECT
    DATE_FORMAT(invoice_date, '%Y-%m') AS month,
    ROUND(SUM(quantity * unit_price), 2) AS monthly_revenue
FROM retail_transactions
GROUP BY month
ORDER BY month;

-- ==================================================
-- Q4a. Best-selling products by quantity sold
-- ==================================================
SELECT
    stock_code,
    MAX(description) AS description,
    SUM(quantity) AS total_quantity_sold
FROM retail_transactions
GROUP BY stock_code
ORDER BY total_quantity_sold DESC
LIMIT 10;

-- ==================================================
-- Q4b. Best-selling products by revenue
-- ==================================================
SELECT
    stock_code,
    MAX(description) AS description,
    ROUND(SUM(quantity * unit_price), 2) AS total_revenue
FROM retail_transactions
GROUP BY stock_code
ORDER BY total_revenue DESC
LIMIT 10;

-- ==================================================
-- Q5. Revenue and customer count by country
-- ==================================================
SELECT
    country,
    COUNT(DISTINCT customer_id) AS num_customers,
    ROUND(SUM(quantity * unit_price), 2) AS total_revenue
FROM retail_transactions
GROUP BY country
ORDER BY total_revenue DESC;

-- ==================================================
-- Q6. Average order value by segment
-- Order value = revenue per invoice; averaged within each segment
-- ==================================================
SELECT
    c.segment,
    ROUND(AVG(invoice_totals.invoice_revenue), 2) AS avg_order_value
FROM rfm_customers c
JOIN (
    SELECT customer_id, invoice, SUM(quantity * unit_price) AS invoice_revenue
    FROM retail_transactions
    GROUP BY customer_id, invoice
) invoice_totals ON invoice_totals.customer_id = c.customer_id
GROUP BY c.segment
ORDER BY avg_order_value DESC;

-- ==================================================
-- Q7. Repeat purchase rate: % of customers with more than 1 invoice
-- ==================================================
SELECT
    COUNT(*) AS total_customers,
    SUM(CASE WHEN invoice_count > 1 THEN 1 ELSE 0 END) AS repeat_customers,
    ROUND(
        SUM(CASE WHEN invoice_count > 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*),
        2
    ) AS repeat_purchase_rate_pct
FROM (
    SELECT customer_id, COUNT(DISTINCT invoice) AS invoice_count
    FROM retail_transactions
    GROUP BY customer_id
) per_customer;

-- ==================================================
-- Q8. Rank customers within each segment by monetary value
-- ==================================================
SELECT
    customer_id,
    segment,
    monetary_value,
    RANK() OVER (PARTITION BY segment ORDER BY monetary_value DESC) AS rank_in_segment
FROM rfm_customers
ORDER BY segment, rank_in_segment;
