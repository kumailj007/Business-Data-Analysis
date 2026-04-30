-- =====================================================================
-- analysis.sql — Business Sales Analysis Queries
-- =====================================================================
-- Author : Kumail Janjua
-- Purpose: SQL equivalents of the Python analysis pipeline. Demonstrates
--          relational thinking and analytical SQL alongside the Pandas
--          implementation in analysis.py.
-- Schema : sales(order_id, customer_id, region, product, category,
--          price, quantity, order_date)
-- =====================================================================


-- ------------------------------------------------------------------
-- 1) Top products by revenue
-- ------------------------------------------------------------------
SELECT
    product,
    SUM(price * quantity)              AS total_revenue,
    SUM(quantity)                      AS units_sold,
    COUNT(*)                           AS order_count
FROM sales
GROUP BY product
ORDER BY total_revenue DESC
LIMIT 10;


-- ------------------------------------------------------------------
-- 2) Revenue by region
-- ------------------------------------------------------------------
SELECT
    region,
    SUM(price * quantity)              AS regional_revenue,
    COUNT(DISTINCT customer_id)        AS unique_customers
FROM sales
GROUP BY region
ORDER BY regional_revenue DESC;


-- ------------------------------------------------------------------
-- 3) Monthly revenue trend
-- ------------------------------------------------------------------
SELECT
    STRFTIME('%Y-%m', order_date)      AS month,
    SUM(price * quantity)              AS monthly_revenue,
    COUNT(*)                           AS orders
FROM sales
GROUP BY month
ORDER BY month;


-- ------------------------------------------------------------------
-- 4) Revenue share by category
-- ------------------------------------------------------------------
SELECT
    category,
    SUM(price * quantity)                                  AS category_revenue,
    ROUND(
        100.0 * SUM(price * quantity)
              / (SELECT SUM(price * quantity) FROM sales),
        2
    )                                                      AS pct_of_total
FROM sales
GROUP BY category
ORDER BY category_revenue DESC;


-- ------------------------------------------------------------------
-- 5) Top 10 customers by lifetime value (retention insight)
-- ------------------------------------------------------------------
SELECT
    customer_id,
    COUNT(*)                           AS orders_placed,
    SUM(price * quantity)              AS lifetime_value,
    ROUND(AVG(price * quantity), 2)    AS avg_order_value
FROM sales
GROUP BY customer_id
ORDER BY lifetime_value DESC
LIMIT 10;


-- ------------------------------------------------------------------
-- 6) Repeat-buyer rate — how many customers ordered more than once?
-- ------------------------------------------------------------------
SELECT
    ROUND(
        100.0 * SUM(CASE WHEN order_count > 1 THEN 1 ELSE 0 END)
              / COUNT(*),
        2
    ) AS repeat_buyer_rate_pct
FROM (
    SELECT customer_id, COUNT(*) AS order_count
    FROM sales
    GROUP BY customer_id
);
