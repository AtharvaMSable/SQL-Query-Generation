-- AskQL Platform Database Schema
-- Sample schema for multi-tenant analytics platform with Neon PostgreSQL

-- ============================================================================
-- 1. USER MANAGEMENT
-- ============================================================================

-- Users table: stores user accounts
CREATE TABLE IF NOT EXISTS users (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,  -- SHA-256 hash (use bcrypt in production)
    full_name VARCHAR(100) NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'analyst',  -- analyst, admin, viewer
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP
);

-- ============================================================================
-- 2. DATASET MANAGEMENT
-- ============================================================================

-- Datasets table: defines available datasets (schemas/table groups)
CREATE TABLE IF NOT EXISTS datasets (
    dataset_id SERIAL PRIMARY KEY,
    dataset_name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    schema_name VARCHAR(50) NOT NULL,  -- PostgreSQL schema containing the data
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- 3. ACCESS CONTROL
-- ============================================================================

-- User-Dataset access mapping: defines which users can access which datasets
CREATE TABLE IF NOT EXISTS user_dataset_access (
    access_id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    dataset_id INTEGER NOT NULL REFERENCES datasets(dataset_id) ON DELETE CASCADE,
    access_level VARCHAR(20) DEFAULT 'read',  -- read, write, admin
    is_active BOOLEAN DEFAULT TRUE,
    granted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    granted_by INTEGER REFERENCES users(user_id),
    UNIQUE(user_id, dataset_id)
);

-- ============================================================================
-- 4. AUDIT & HISTORY
-- ============================================================================

-- Query history: logs all queries for audit and analytics
CREATE TABLE IF NOT EXISTS query_history (
    query_id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    dataset_id INTEGER NOT NULL REFERENCES datasets(dataset_id) ON DELETE CASCADE,
    question TEXT NOT NULL,  -- Natural language question
    generated_sql TEXT NOT NULL,  -- Generated SQL query
    row_count INTEGER,
    execution_time_ms INTEGER,
    status VARCHAR(20) DEFAULT 'success',  -- success, error
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- 5. SAMPLE DATA SCHEMA: SALES ANALYTICS
-- ============================================================================

-- Create a sample schema for demonstration
CREATE SCHEMA IF NOT EXISTS sales_data;

-- Products table
CREATE TABLE IF NOT EXISTS sales_data.products (
    product_id SERIAL PRIMARY KEY,
    product_name VARCHAR(100) NOT NULL,
    category VARCHAR(50),
    unit_price DECIMAL(10, 2),
    cost DECIMAL(10, 2),
    supplier VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Customers table
CREATE TABLE IF NOT EXISTS sales_data.customers (
    customer_id SERIAL PRIMARY KEY,
    customer_name VARCHAR(100) NOT NULL,
    email VARCHAR(100),
    phone VARCHAR(20),
    city VARCHAR(50),
    state VARCHAR(50),
    country VARCHAR(50) DEFAULT 'USA',
    segment VARCHAR(20),  -- Enterprise, SMB, Individual
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Sales transactions table
CREATE TABLE IF NOT EXISTS sales_data.sales (
    sale_id SERIAL PRIMARY KEY,
    product_id INTEGER REFERENCES sales_data.products(product_id),
    customer_id INTEGER REFERENCES sales_data.customers(customer_id),
    order_date DATE NOT NULL,
    quantity INTEGER NOT NULL,
    unit_price DECIMAL(10, 2) NOT NULL,
    discount_percent DECIMAL(5, 2) DEFAULT 0,
    revenue DECIMAL(12, 2) GENERATED ALWAYS AS (quantity * unit_price * (1 - discount_percent / 100)) STORED,
    region VARCHAR(50),
    sales_rep VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- 6. INSERT SAMPLE USERS
-- ============================================================================

-- Sample users (password: 'demo123' hashed with SHA-256)
-- In production, use bcrypt or argon2
INSERT INTO users (username, email, password_hash, full_name, role, is_active)
VALUES 
    ('admin', 'admin@askql.com', 
     'd3ad9315b7be5dd53b31a273b3b3aba5defe700808305aa16a3062b76658a791',  -- demo123
     'Admin User', 'admin', TRUE),
    
    ('analyst1', 'analyst1@askql.com',
     'd3ad9315b7be5dd53b31a273b3b3aba5defe700808305aa16a3062b76658a791',  -- demo123
     'John Analyst', 'analyst', TRUE),
    
    ('viewer1', 'viewer1@askql.com',
     'd3ad9315b7be5dd53b31a273b3b3aba5defe700808305aa16a3062b76658a791',  -- demo123
     'Jane Viewer', 'viewer', TRUE)
ON CONFLICT (username) DO UPDATE SET password_hash = EXCLUDED.password_hash;

-- ============================================================================
-- 7. INSERT SAMPLE DATASETS
-- ============================================================================

INSERT INTO datasets (dataset_name, description, schema_name, is_active)
VALUES 
    ('Sales Analytics', 'Sales transactions, products, and customer data', 'sales_data', TRUE),
    ('Public Data', 'Publicly accessible datasets', 'public', TRUE)
ON CONFLICT (dataset_name) DO NOTHING;

-- ============================================================================
-- 8. GRANT ACCESS TO USERS
-- ============================================================================

-- Admin gets access to all datasets
INSERT INTO user_dataset_access (user_id, dataset_id, access_level, is_active)
SELECT u.user_id, d.dataset_id, 'admin', TRUE
FROM users u
CROSS JOIN datasets d
WHERE u.username = 'admin'
ON CONFLICT (user_id, dataset_id) DO NOTHING;

-- Analyst gets read access to Sales Analytics
INSERT INTO user_dataset_access (user_id, dataset_id, access_level, is_active)
SELECT u.user_id, d.dataset_id, 'read', TRUE
FROM users u
CROSS JOIN datasets d
WHERE u.username = 'analyst1' AND d.dataset_name = 'Sales Analytics'
ON CONFLICT (user_id, dataset_id) DO NOTHING;

-- Viewer gets read access to Sales Analytics
INSERT INTO user_dataset_access (user_id, dataset_id, access_level, is_active)
SELECT u.user_id, d.dataset_id, 'read', TRUE
FROM users u
CROSS JOIN datasets d
WHERE u.username = 'viewer1' AND d.dataset_name = 'Sales Analytics'
ON CONFLICT (user_id, dataset_id) DO NOTHING;

-- ============================================================================
-- 9. INSERT SAMPLE DATA: PRODUCTS
-- ============================================================================

INSERT INTO sales_data.products (product_name, category, unit_price, cost, supplier, is_active)
VALUES 
    ('Widget Pro', 'Electronics', 299.99, 150.00, 'TechSupply Inc', TRUE),
    ('Gadget Plus', 'Electronics', 199.99, 100.00, 'TechSupply Inc', TRUE),
    ('Premium Widget', 'Electronics', 499.99, 250.00, 'EliteSupply', TRUE),
    ('Basic Tool', 'Hardware', 49.99, 25.00, 'ToolMasters', TRUE),
    ('Pro Tool', 'Hardware', 149.99, 75.00, 'ToolMasters', TRUE),
    ('Office Chair', 'Furniture', 249.99, 120.00, 'FurnitureHub', TRUE),
    ('Standing Desk', 'Furniture', 599.99, 300.00, 'FurnitureHub', TRUE),
    ('Laptop Bag', 'Accessories', 79.99, 35.00, 'BagWorld', TRUE),
    ('USB-C Hub', 'Accessories', 39.99, 15.00, 'TechSupply Inc', TRUE),
    ('Wireless Mouse', 'Accessories', 29.99, 12.00, 'TechSupply Inc', TRUE)
ON CONFLICT DO NOTHING;

-- ============================================================================
-- 10. INSERT SAMPLE DATA: CUSTOMERS
-- ============================================================================

INSERT INTO sales_data.customers (customer_name, email, phone, city, state, country, segment)
VALUES 
    ('Acme Corporation', 'sales@acme.com', '555-0101', 'New York', 'NY', 'USA', 'Enterprise'),
    ('TechStart Inc', 'info@techstart.com', '555-0102', 'San Francisco', 'CA', 'USA', 'SMB'),
    ('Global Systems', 'contact@globalsys.com', '555-0103', 'Chicago', 'IL', 'USA', 'Enterprise'),
    ('Small Business Co', 'hello@smallbiz.com', '555-0104', 'Austin', 'TX', 'USA', 'SMB'),
    ('Individual Buyer 1', 'buyer1@email.com', '555-0105', 'Seattle', 'WA', 'USA', 'Individual'),
    ('Individual Buyer 2', 'buyer2@email.com', '555-0106', 'Boston', 'MA', 'USA', 'Individual'),
    ('Enterprise Tech', 'sales@enttech.com', '555-0107', 'Los Angeles', 'CA', 'USA', 'Enterprise'),
    ('MidSize Corp', 'info@midsize.com', '555-0108', 'Denver', 'CO', 'USA', 'SMB'),
    ('Startup Hub', 'hello@startuphub.com', '555-0109', 'Portland', 'OR', 'USA', 'SMB'),
    ('Big Company Ltd', 'contact@bigco.com', '555-0110', 'Miami', 'FL', 'USA', 'Enterprise')
ON CONFLICT DO NOTHING;

-- ============================================================================
-- 11. INSERT SAMPLE DATA: SALES TRANSACTIONS (Last 12 months)
-- ============================================================================

-- Generate sales data for the past 12 months
INSERT INTO sales_data.sales (product_id, customer_id, order_date, quantity, unit_price, discount_percent, region, sales_rep)
SELECT 
    (random() * 9 + 1)::INTEGER,  -- Random product 1-10
    (random() * 9 + 1)::INTEGER,  -- Random customer 1-10
    (CURRENT_DATE - (random() * 365)::INTEGER),  -- Random date in last year
    (random() * 10 + 1)::INTEGER,  -- Quantity 1-10
    (50 + random() * 500)::NUMERIC(10,2),  -- Price $50-$550
    (random() * 20)::NUMERIC(5,2),  -- Discount 0-20%
    CASE (random() * 3)::INTEGER
        WHEN 0 THEN 'East'
        WHEN 1 THEN 'West'
        WHEN 2 THEN 'Central'
        ELSE 'South'
    END,
    CASE (random() * 4)::INTEGER
        WHEN 0 THEN 'Alice Johnson'
        WHEN 1 THEN 'Bob Smith'
        WHEN 2 THEN 'Carol Davis'
        WHEN 3 THEN 'David Wilson'
        ELSE 'Eve Martinez'
    END
FROM generate_series(1, 500);  -- Generate 500 sample transactions

-- ============================================================================
-- 12. CREATE INDEXES FOR PERFORMANCE
-- ============================================================================

-- Indexes on foreign keys
CREATE INDEX IF NOT EXISTS idx_user_dataset_access_user ON user_dataset_access(user_id);
CREATE INDEX IF NOT EXISTS idx_user_dataset_access_dataset ON user_dataset_access(dataset_id);
CREATE INDEX IF NOT EXISTS idx_query_history_user ON query_history(user_id);
CREATE INDEX IF NOT EXISTS idx_query_history_dataset ON query_history(dataset_id);
CREATE INDEX IF NOT EXISTS idx_query_history_created ON query_history(created_at DESC);

-- Indexes on sales data for query performance
CREATE INDEX IF NOT EXISTS idx_sales_order_date ON sales_data.sales(order_date);
CREATE INDEX IF NOT EXISTS idx_sales_product ON sales_data.sales(product_id);
CREATE INDEX IF NOT EXISTS idx_sales_customer ON sales_data.sales(customer_id);
CREATE INDEX IF NOT EXISTS idx_sales_region ON sales_data.sales(region);

-- ============================================================================
-- 13. CREATE VIEWS FOR COMMON QUERIES
-- ============================================================================

-- Sales summary view
CREATE OR REPLACE VIEW sales_data.sales_summary AS
SELECT 
    s.sale_id,
    s.order_date,
    p.product_name,
    p.category,
    c.customer_name,
    c.segment,
    s.quantity,
    s.unit_price,
    s.discount_percent,
    s.revenue,
    s.region,
    s.sales_rep
FROM sales_data.sales s
LEFT JOIN sales_data.products p ON s.product_id = p.product_id
LEFT JOIN sales_data.customers c ON s.customer_id = c.customer_id;

-- ============================================================================
-- SETUP COMPLETE
-- ============================================================================

-- Display summary
DO $$
DECLARE
    user_count INTEGER;
    dataset_count INTEGER;
    access_count INTEGER;
    sales_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO user_count FROM users;
    SELECT COUNT(*) INTO dataset_count FROM datasets;
    SELECT COUNT(*) INTO access_count FROM user_dataset_access;
    SELECT COUNT(*) INTO sales_count FROM sales_data.sales;
    
    RAISE NOTICE '========================================';
    RAISE NOTICE 'AskQL Database Setup Complete!';
    RAISE NOTICE '========================================';
    RAISE NOTICE 'Users created: %', user_count;
    RAISE NOTICE 'Datasets created: %', dataset_count;
    RAISE NOTICE 'Access grants: %', access_count;
    RAISE NOTICE 'Sample sales records: %', sales_count;
    RAISE NOTICE '========================================';
    RAISE NOTICE 'Demo Login Credentials:';
    RAISE NOTICE '  Username: admin | Password: demo123';
    RAISE NOTICE '  Username: analyst1 | Password: demo123';
    RAISE NOTICE '  Username: viewer1 | Password: demo123';
    RAISE NOTICE '========================================';
END $$;
