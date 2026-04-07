## PL

# Variables
# Cursor (like an interator)
DECLARE prod_cursor CURSOR FOR
    SELECT product_id, price FROM products;


# Control Flow

# Branching
# If/ELSE
# CASE

IF balance < 0 THEN
    SET status = 'OVERDRAWN';
ELSEIF balance = 0 THEN
    SET status = 'ZERO';
ELSE
    SET status = 'POSITIVE';
END IF;

-- Simple CASE
CASE department_id
    WHEN 10 THEN SET dept_name = 'Finance';
    WHEN 20 THEN SET dept_name = 'Engineering';
    ELSE SET dept_name = 'Other';
END CASE;

-- Searched CASE
CASE
    WHEN salary > 100000 THEN SET tier = 'Senior';
    WHEN salary > 60000 THEN SET tier = 'Mid';
    ELSE SET tier = 'Junior';
END CASE;





# Loops
# LOOP
# WHILE
# REPEAT


-- LOOP: infinite loop, exit with LEAVE
my_loop: LOOP
    SET counter = counter + 1;
    IF counter >= 10 THEN
        LEAVE my_loop;
    END IF;
END LOOP my_loop;



-- WHILE: checks condition before each iteration
WHILE counter < 10 DO
    SET counter = counter + 1;
END WHILE;


-- REPEAT: checks condition after each iteration (always runs at least once)
REPEAT
    SET counter = counter + 1;
UNTIL counter >= 10
END REPEAT;




# Jumps / Functions
# Stored procedures
# user defined functions

# User-defined function

DELIMITER //
 
CREATE FUNCTION calculate_discount_price(
    unit_price DECIMAL(10,2),
    quantity INT
)
RETURNS DECIMAL(10,2)
DETERMINISTIC # deterministic: pure function - no side effects - the same input will always produce the same output
BEGIN
    DECLARE discount_rate DECIMAL(3,2);
 
    CASE
        WHEN quantity >= 100 THEN SET discount_rate = 0.30;
        WHEN quantity >= 50  THEN SET discount_rate = 0.20;
        WHEN quantity >= 10  THEN SET discount_rate = 0.10;
        ELSE SET discount_rate = 0.00;
    END CASE;
 
    RETURN unit_price * quantity * (1 - discount_rate);
END //
 
DELIMITER ;




-- Basic usage: call it with literal values
SELECT calculate_discount_price(29.99, 5)   AS small_order,
       calculate_discount_price(29.99, 25)  AS medium_order,
       calculate_discount_price(29.99, 75)  AS large_order,
       calculate_discount_price(29.99, 150) AS bulk_order;
 
-- Use it inline with table data
-- (assumes an order_items table with unit_price and quantity columns)
SELECT order_id,
       product_name,
       unit_price,
       quantity,
       unit_price * quantity                          AS subtotal_before,
       calculate_discount_price(unit_price, quantity) AS subtotal_after
FROM order_items;
 
-- Use it in a WHERE clause to find orders where discount savings exceed $50
SELECT order_id,
       unit_price * quantity AS full_price,
       calculate_discount_price(unit_price, quantity) AS discounted_price
FROM order_items
WHERE (unit_price * quantity) - calculate_discount_price(unit_price, quantity) > 50;





# Stored procedure

DELIMITER //

CREATE PROCEDURE get_employee_by_dept(IN dept_id INT)
BEGIN
    SELECT employee_id, first_name, last_name, salary
    FROM employees
    WHERE department_id = dept_id;
END //

DELIMITER ;




DELIMITER //

CREATE PROCEDURE count_by_dept(IN dept_id INT, OUT total INT)
BEGIN
    SELECT COUNT(*) INTO total
    FROM employees
    WHERE department_id = dept_id;
END //

DELIMITER ;

-- Usage:
CALL count_by_dept(10, @result);
SELECT @result;


