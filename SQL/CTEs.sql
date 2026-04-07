# Example CTEs


WITH recent_orders AS (
    SELECT order_id, customer_id, order_date, total
    FROM orders
    WHERE order_date >= '2025-01-01'
)
SELECT customer_id, COUNT(*) AS order_count, SUM(total) AS total_spent
FROM recent_orders
GROUP BY customer_id;




WITH RECURSIVE org_chart AS (
    -- Anchor: start with the CEO (no manager)
    SELECT employee_id, name, manager_id, 0 AS depth
    FROM employees
    WHERE manager_id IS NULL

    UNION ALL

    -- Recursive: find each employee's direct reports
    SELECT e.employee_id, e.name, e.manager_id, oc.depth + 1
    FROM employees e
    JOIN org_chart oc ON e.manager_id = oc.employee_id
)
SELECT employee_id, name, depth
FROM org_chart
ORDER BY depth, name;

