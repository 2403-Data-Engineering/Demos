-- ============================================================
-- Trigger Demo: Product Price Audit Log
-- ============================================================
-- Scenario: A products table where we want to automatically
-- track every price change — who changed it, when, and what
-- the old and new values were.
-- ============================================================
 
-- Setup
CREATE TABLE products (
    product_id INT PRIMARY KEY,
    product_name VARCHAR(100),
    price DECIMAL(10,2)
);
 
CREATE TABLE price_audit_log (
    audit_id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT,
    product_name VARCHAR(100),
    old_price DECIMAL(10,2),
    new_price DECIMAL(10,2),
    change_pct DECIMAL(5,2),
    changed_at DATETIME
);
 
INSERT INTO products VALUES
(1, 'Wireless Mouse',     29.99),
(2, 'Mechanical Keyboard', 89.99),
(3, 'USB-C Hub',           45.00),
(4, 'Monitor Stand',       34.50);
 
-- ============================================================
-- The Trigger
-- ============================================================
-- Fires AFTER an UPDATE on the products table.
-- Only logs a row if the price actually changed.
 
CREATE TRIGGER after_price_update
AFTER UPDATE ON products
FOR EACH ROW
BEGIN
    IF OLD.price <> NEW.price THEN
        INSERT INTO price_audit_log (product_id, product_name, old_price, new_price, change_pct, changed_at)
        VALUES (
            OLD.product_id,
            OLD.product_name,
            OLD.price,
            NEW.price,
            ROUND(((NEW.price - OLD.price) / OLD.price) * 100, 2),
            NOW()
        );
    END IF;
END;
 
-- ============================================================
-- Test it out
-- ============================================================
 
-- Price increase
UPDATE products SET price = 34.99 WHERE product_id = 1;
 
-- Price decrease
UPDATE products SET price = 79.99 WHERE product_id = 2;
 
-- Update that doesn't touch price — should NOT create a log entry
UPDATE products SET product_name = 'USB-C Hub (7-port)' WHERE product_id = 3;
 
-- Bulk update
UPDATE products SET price = price * 1.10;
 
-- Check the audit log
SELECT * FROM price_audit_log ORDER BY audit_id;