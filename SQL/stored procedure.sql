-- ============================================================
-- Stored Procedure Example: apply_raise
-- ============================================================
-- Scenario: HR passes in a raise percentage. The procedure
-- applies it to an employee's salary and sends back the
-- new salary through the same INOUT parameter.
--
-- This demonstrates INOUT: the parameter carries a value IN
-- (the raise percentage), gets overwritten inside the
-- procedure, and carries a different value OUT (the new salary).
-- ============================================================

DELIMITER //

CREATE PROCEDURE apply_raise(
    IN emp_id INT,
    INOUT amount DECIMAL(10,2)
)
BEGIN
    DECLARE current_salary DECIMAL(10,2);

    SELECT salary INTO current_salary
    FROM employees
    WHERE employee_id = emp_id;

    -- amount comes in as a percentage (e.g. 5.00 = 5%)
    -- calculate the new salary
    SET current_salary = current_salary * (1 + amount / 100);

    UPDATE employees
    SET salary = current_salary
    WHERE employee_id = emp_id;

    -- overwrite amount with the new salary to send it back out
    SET amount = current_salary;
END //

DELIMITER ;

-- ============================================================
-- Demo usage
-- ============================================================

-- Set @val to the raise percentage (5%)
SET @val = 5.00;

-- Call the procedure — @val goes in as 5.00 (the raise %)
CALL apply_raise(101, @val);

-- After the call, @val now holds the employee's new salary
SELECT @val AS new_salary;
