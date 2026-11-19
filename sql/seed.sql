
INSERT INTO customers (name, email, signup_date)
VALUES
    ('Alice', 'alice@example.com', '2026-01-10'),
    ('Bob', 'bob@example.com', '2026-02-15'),
    ('Charlie', 'charlie@example.com', '2026-03-20')
ON CONFLICT (email) DO NOTHING;

INSERT INTO products (name, price)
VALUES
    ('Laptop', 900.00),
    ('Keyboard', 50.00),
    ('Mouse', 25.00),
    ('Monitor', 250.00);
