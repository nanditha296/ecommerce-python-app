from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3, os

app = Flask(__name__)
app.secret_key = "secret-key-123"  # You can change this to any random string

# -------------------------------------------------------
# DATABASE CONNECTION
# -------------------------------------------------------
def get_db_connection():
    conn = sqlite3.connect("database/products.db")
    conn.row_factory = sqlite3.Row
    return conn

# -------------------------------------------------------
# INITIALIZE DATABASE (Run Once)
# -------------------------------------------------------
def init_db():
    os.makedirs("database", exist_ok=True)
    conn = get_db_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price REAL NOT NULL,
            stock INTEGER DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()

# -------------------------------------------------------
# HOME PAGE – DISPLAY PRODUCTS
# -------------------------------------------------------
@app.route("/")
def index():
    conn = get_db_connection()
    products = conn.execute("SELECT * FROM products").fetchall()
    conn.close()
    return render_template("index.html", products=products)

# -------------------------------------------------------
# ADD TO CART
# -------------------------------------------------------
@app.route("/add_to_cart/<int:product_id>")
def add_to_cart(product_id):
    conn = get_db_connection()
    product = conn.execute("SELECT * FROM products WHERE id = ?", (product_id,)).fetchone()
    conn.close()

    if not product:
        return redirect(url_for("index"))

    cart = session.get("cart", [])
    found = False

    for item in cart:
        if item["id"] == product["id"]:
            item["quantity"] += 1
            found = True
            break

    if not found:
        cart.append({
            "id": product["id"],
            "name": product["name"],
            "price": float(product["price"]),
            "quantity": 1
        })

    session["cart"] = cart
    session.modified = True
    return redirect(url_for("cart"))

# -------------------------------------------------------
# VIEW CART
# -------------------------------------------------------
@app.route("/cart")
def cart():
    cart = session.get("cart", [])
    total = sum(item["price"] * item["quantity"] for item in cart)
    return render_template("cart.html", cart=cart, total=total)

# -------------------------------------------------------
# UPDATE QUANTITY
# -------------------------------------------------------
@app.route("/update_quantity/<int:product_id>/<action>")
def update_quantity(product_id, action):
    cart = session.get("cart", [])
    for item in cart:
        if item["id"] == product_id:
            if action == "increase":
                item["quantity"] += 1
            elif action == "decrease" and item["quantity"] > 1:
                item["quantity"] -= 1
            break
    session["cart"] = cart
    session.modified = True
    return redirect(url_for("cart"))

# -------------------------------------------------------
# REMOVE FROM CART
# -------------------------------------------------------
@app.route("/remove_from_cart/<int:product_id>")
def remove_from_cart(product_id):
    cart = session.get("cart", [])
    cart = [item for item in cart if item["id"] != product_id]
    session["cart"] = cart
    session.modified = True
    return redirect(url_for("cart"))

# -------------------------------------------------------
# CHECKOUT
# -------------------------------------------------------
@app.route("/checkout", methods=["GET", "POST"])
def checkout():
    if request.method == "POST":
        payment_type = request.form.get("payment_type")
        total = float(request.form.get("total", 0))
        session.pop("cart", None)
        return render_template("checkout.html", total=total, payment_type=payment_type)
    else:
        cart = session.get("cart", [])
        total = sum(item["price"] * item["quantity"] for item in cart)
        return render_template("checkout.html", total=total, payment_type=None)

# -------------------------------------------------------
# ADMIN LOGIN
# -------------------------------------------------------
@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if username == "admin" and password == "admin123":
            session["admin_logged_in"] = True
            return redirect(url_for("manage_products"))
        else:
            return render_template("admin_login.html", error="Invalid credentials")

    return render_template("admin_login.html", error=None)

# -------------------------------------------------------
# ADMIN LOGOUT
# -------------------------------------------------------
@app.route("/admin/logout")
def admin_logout():
    session.pop("admin_logged_in", None)
    return redirect(url_for("admin_login"))

# -------------------------------------------------------
# ADMIN - ADD PRODUCT
# -------------------------------------------------------
@app.route("/admin/add_product", methods=["GET", "POST"])
def add_product():
    if not session.get("admin_logged_in"):
        return redirect(url_for("admin_login"))

    if request.method == "POST":
        name = request.form["name"]
        price = float(request.form["price"])
        stock = int(request.form["stock"])

        conn = get_db_connection()
        conn.execute("INSERT INTO products (name, price, stock) VALUES (?, ?, ?)",
                     (name, price, stock))
        conn.commit()
        conn.close()

        return redirect(url_for("manage_products"))

    return render_template("add_product.html")

# -------------------------------------------------------
# ADMIN - MANAGE PRODUCTS
# -------------------------------------------------------
@app.route("/admin/manage_products")
def manage_products():
    if not session.get("admin_logged_in"):
        return redirect(url_for("admin_login"))

    conn = get_db_connection()
    products = conn.execute("SELECT * FROM products").fetchall()
    conn.close()
    return render_template("manage_products.html", products=products)

# -------------------------------------------------------
# ADMIN - DELETE PRODUCT
# -------------------------------------------------------
@app.route("/admin/delete_product/<int:product_id>")
def delete_product(product_id):
    if not session.get("admin_logged_in"):
        return redirect(url_for("admin_login"))

    conn = get_db_connection()
    conn.execute("DELETE FROM products WHERE id = ?", (product_id,))
    conn.commit()
    conn.close()
    return redirect(url_for("manage_products"))

# -------------------------------------------------------
# START APP
# -------------------------------------------------------
if __name__ == "__main__":
    init_db()  # Ensure DB and table exist
    app.run(debug=True)
