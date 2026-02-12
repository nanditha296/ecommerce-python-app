import sqlite3, os

os.makedirs("database", exist_ok=True)
conn = sqlite3.connect("database/products.db")
c = conn.cursor()

# Drop and recreate table
c.execute("DROP TABLE IF EXISTS products")
c.execute("""
CREATE TABLE products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    price REAL NOT NULL,
    description TEXT
)
""")

# Insert sample data
products = [
    ("Laptop", 899.99, "High performance laptop"),
    ("Smartphone", 499.99, "Latest Android phone"),
    ("Headphones", 89.99, "Noise-cancelling headphones"),
    ("Office Chair", 149.99, "Ergonomic chair for long hours")
]
c.executemany("INSERT INTO products (name, price, description) VALUES (?, ?, ?)", products)

conn.commit()
conn.close()
print("✅ Database successfully initialized!")
