# Window functions


CREATE TABLE employees (
    employee_id INT PRIMARY KEY,
    employee_name VARCHAR(100),
    department VARCHAR(50),
    salary DECIMAL(10,2)
);

INSERT INTO employees VALUES
(1,  'Alice Chen',      'Engineering', 95000.00),
(2,  'Bob Martinez',    'Engineering', 88000.00),
(3,  'Carol Johnson',   'Engineering', 72000.00),
(4,  'David Kim',       'Sales',       65000.00),
(5,  'Emma Wilson',     'Sales',       70000.00),
(6,  'Frank Lee',       'Sales',       62000.00),
(7,  'Grace Patel',     'Marketing',   78000.00),
(8,  'Hank Thomas',     'Marketing',   71000.00);

-- Total salary across the entire table, attached to every row
SELECT employee_id, department, salary,
       SUM(salary) OVER(PARTITION BY department) AS total_salary
FROM employees;

# similarly we could group by, but that hides some data from the result set
SELECT employee_id, department, salary, SUM(salary) AS Total
FROM employees
GROUP BY department








CREATE TABLE monthly_revenue (
    month DATE PRIMARY KEY,
    revenue DECIMAL(10,2)
);
 
INSERT INTO monthly_revenue VALUES
('2025-01-01',  42000.00),
('2025-02-01',  38500.00),
('2025-03-01',  45200.00),
('2025-04-01',  47800.00),
('2025-05-01',  44100.00),
('2025-06-01',  51300.00),
('2025-07-01',  53900.00),
('2025-08-01',  49700.00),
('2025-09-01',  56200.00),
('2025-10-01',  58400.00),
('2025-11-01',  62100.00),
('2025-12-01',  71500.00);





-- Compare each month's revenue to the previous month
SELECT month, revenue,
       LAG(revenue, 4) OVER(ORDER BY month) AS prev_month,
       revenue - LAG(revenue, 1) OVER(ORDER BY month) AS month_over_month,
       LEAD(revenue, 1) OVER(ORDER BY month) AS next_month
FROM monthly_revenue;





-- 3-month moving average
SELECT month, revenue,
       AVG(revenue) OVER(
           ORDER BY month
           ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
       ) AS moving_avg_3m
FROM monthly_revenue;

# Other examples of OVER windows:
ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
ROWS BETWEEN 2 PRECEDING AND 2 FOLLOWING
ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING

-- UNBOUNDED PRECEDING — the first row of the partition
-- n PRECEDING — n rows before the current row
-- CURRENT ROW — the current row
-- n FOLLOWING — n rows after the current row
-- UNBOUNDED FOLLOWING — the last row of the partition

