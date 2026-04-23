import os
import sqlite3
from flask import Flask, request, redirect, url_for, session, flash
from markupsafe import Markup, escape

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'change-me-in-production')  # nosemgrep
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

@app.route('/')
def home():
    logged_in_user = session.get('username')
    current_user = None

    conn = get_db_connection()

    if logged_in_user:
        current_user = conn.execute(
            "SELECT * FROM users WHERE username = ?", (logged_in_user,)
        ).fetchone()

    products = conn.execute('SELECT * FROM products').fetchall()
    conn.close()

    greeting = Markup("Welcome to My Shop!")
    if current_user:
        greeting = Markup("Welcome to My Shop, {}!").format(escape(current_user['username']))

    nav = Markup(
        "<!DOCTYPE html><html><head>"
        "<title>My Shop</title>"
        "</head><body>"
    ) + Markup("<h1>{}</h1><nav>"
               "<a href='{}'>Home</a> | "
               "<a href='{}'>About</a>").format(
        greeting,
        url_for('home'),
        url_for('about')
    )

    if current_user:
        nav += Markup(" | <a href='{}'>Logout</a>").format(url_for('logout'))
        if current_user['is_admin']:
            nav += Markup(" | <a href='{}'>Admin Panel</a>").format(url_for('admin_panel'))
        if current_user['is_seller'] or current_user['is_admin']:
            nav += Markup(" | <a href='{}'>Add a Product</a>").format(url_for('add_product'))
        else:
            nav += Markup(" | <a href='{}'>Become a Seller</a>").format(url_for('become_seller'))
    else:
        nav += Markup(" | <a href='{}'>Login</a> | <a href='{}'>Register</a>").format(
            url_for('login'), url_for('register')
        )

    nav += Markup("</nav><hr><h2>Products</h2>")

    for product in products:
        nav += Markup(
            "<div><h2><a href='{}'>{}</a></h2>"
            "<p><strong>Price:</strong> £{} | <strong>Seller:</strong> {}</p>"
            "<p>{}</p></div><hr>"
        ).format(
            url_for('product_page', product_id=product['id']),
            escape(product['name']),
            escape(str(product['price'])),
            escape(product['seller_name']),
            escape(product['description'])
        )

    nav += Markup("</body></html>")
    return nav

@app.route('/about')
def about():
    return Markup(
        "<!DOCTYPE html><html><head><title>About Us</title></head>"
        "<body><h1>About Our Shop</h1>"
        "<p>This is the page where we talk about ourselves.</p>"
        "<a href='/'>Go back home</a></body></html>"
    )

@app.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        try:
            conn.execute(
                "INSERT INTO users (username, password) VALUES (?, ?)",
                (username, password)
            )
            conn.commit()
        except conn.IntegrityError:
            flash("Username already exists. Please choose another.")
            conn.close()
            return redirect(url_for('register'))

        conn.close()
        flash("Registration successful! Please log in.")
        return redirect(url_for('login'))

    return Markup(
        "<!DOCTYPE html><html><head><title>Register</title></head><body>"
        "<h1>Register for an Account</h1>"
        "<form method='post'>"
        "<label for='username'>Username</label>"
        "<input type='text' name='username' id='username' required><br>"
        "<label for='password'>Password</label>"
        "<input type='password' name='password' id='password' required><br>"
        "<button type='submit'>Register</button>"
        "</form></body></html>"
    )

@app.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        user = conn.execute(
            "SELECT * FROM users WHERE username = ? AND password = ?",
            (username, password)
        ).fetchone()
        conn.close()

        if user:
            session['username'] = user['username']
            return redirect(url_for('home'))

        flash('Incorrect username or password.')
        return redirect(url_for('login'))

    return Markup(
        "<!DOCTYPE html><html><head><title>Login</title></head><body>"
        "<h1>Login</h1>"
        "<form method='post'>"
        "<label for='username'>Username</label>"
        "<input type='text' name='username' id='username' required><br>"
        "<label for='password'>Password</label>"
        "<input type='password' name='password' id='password' required><br>"
        "<button type='submit'>Login</button>"
        "</form></body></html>"
    )

@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('You have been logged out.')
    return redirect(url_for('login'))

@app.route('/become_seller', methods=('GET', 'POST'))
def become_seller():
    logged_in_user = session.get('username')
    if not logged_in_user:
        flash("You must be logged in to do this.")
        return redirect(url_for('login'))

    conn = get_db_connection()

    if request.method == 'POST':
        conn.execute(
            "UPDATE users SET is_seller = 1 WHERE username = ?",
            (logged_in_user,)
        )
        conn.commit()
        conn.close()
        flash("Congratulations, you are now a seller!")
        return redirect(url_for('home'))

    conn.close()
    page = Markup(
        "<!DOCTYPE html><html><body>"
        "<h1>Become a Seller</h1>"
        "<p>Click the button below to upgrade your account to a seller account.</p>"
        "<form method='post'><button type='submit'>Become a Seller</button></form><br>"
        "<a href='{}'>Go back</a>"
        "</body></html>"
    ).format(url_for('home'))
    return page

@app.route('/add', methods=('GET', 'POST'))
def add_product():
    logged_in_user = session.get('username')
    if not logged_in_user:
        flash("You need to be logged in.")
        return redirect(url_for('login'))

    conn = get_db_connection()
    user = conn.execute(
        "SELECT * FROM users WHERE username = ?", (logged_in_user,)
    ).fetchone()

    if not (user['is_seller'] or user['is_admin']):
        flash("You must be a seller or admin to add products.")
        conn.close()
        return redirect(url_for('home'))

    if request.method == 'POST':
        name = request.form['name']
        price = request.form['price']
        description = request.form['description']

        conn.execute(
            "INSERT INTO products (name, price, description, seller_name) VALUES (?, ?, ?, ?)",
            (name, price, description, logged_in_user)
        )
        conn.commit()
        conn.close()

        flash("Product listed successfully!")
        return redirect(url_for('home'))

    conn.close()
    return Markup(
        "<!DOCTYPE html><html><body>"
        "<h1>List a New Product</h1>"
        "<form method='post'>"
        "<label for='name'>Product Name</label>"
        "<input type='text' name='name' id='name' required><br>"
        "<label for='price'>Price</label>"
        "<input type='number' step='0.01' name='price' id='price' required><br>"
        "<label for='description'>Description</label>"
        "<textarea name='description' id='description' required></textarea><br>"
        "<button type='submit'>List Product</button>"
        "</form><br><a href='/'>Cancel</a></body></html>"
    )

@app.route('/edit/<int:product_id>', methods=('GET', 'POST'))
def edit_product(product_id):
    logged_in_user = session.get('username')
    if not logged_in_user:
        flash("You need to be logged in.")
        return redirect(url_for('login'))

    conn = get_db_connection()
    user = conn.execute(
        "SELECT * FROM users WHERE username = ?", (logged_in_user,)
    ).fetchone()

    if not (user['is_seller'] or user['is_admin']):
        flash("You must be a seller or admin to manage products.")
        conn.close()
        return redirect(url_for('home'))

    if request.method == 'POST':
        name = request.form['name']
        price = request.form['price']
        description = request.form['description']

        conn.execute(
            "UPDATE products SET name = ?, price = ?, description = ? WHERE id = ?",
            (name, price, description, product_id)
        )
        conn.commit()
        conn.close()

        flash("Product updated successfully!")
        return redirect(url_for('home'))

    product = conn.execute(
        "SELECT * FROM products WHERE id = ?", (product_id,)
    ).fetchone()
    conn.close()

    if not product:
        flash("Product not found.")
        return redirect(url_for('home'))

    page = Markup(
        "<!DOCTYPE html><html><body>"
        "<h1>Edit Product: {}</h1>"
        "<form method='post'>"
        "<label for='name'>Product Name</label>"
        "<input type='text' name='name' id='name' value='{}' required><br>"
        "<label for='price'>Price</label>"
        "<input type='number' step='0.01' name='price' id='price' value='{}' required><br>"
        "<label for='description'>Description</label>"
        "<textarea name='description' id='description' required>{}</textarea><br>"
        "<button type='submit'>Save Changes</button>"
        "</form><br>"
        "<a href='{}'>Cancel</a>"
        "</body></html>"
    ).format(
        escape(product['name']),
        escape(product['name']),
        escape(str(product['price'])),
        escape(product['description']),
        url_for('home')
    )
    return page

@app.route('/delete/<int:product_id>')
def delete_product(product_id):
    logged_in_user = session.get('username')
    if not logged_in_user:
        flash("You need to be logged in.")
        return redirect(url_for('login'))

    conn = get_db_connection()
    user = conn.execute(
        "SELECT * FROM users WHERE username = ?", (logged_in_user,)
    ).fetchone()

    if not (user['is_seller'] or user['is_admin']):
        flash("You must be a seller or admin to manage products.")
        conn.close()
        return redirect(url_for('home'))

    conn.execute("DELETE FROM products WHERE id = ?", (product_id,))
    conn.commit()
    conn.close()

    flash("Product deleted successfully.")
    return redirect(url_for('home'))

@app.route('/product/<int:product_id>', methods=('GET', 'POST'))
def product_page(product_id):
    logged_in_user = session.get('username')
    current_user = None

    conn = get_db_connection()

    if logged_in_user:
        current_user = conn.execute(
            "SELECT * FROM users WHERE username = ?", (logged_in_user,)
        ).fetchone()

    if request.method == 'POST':
        if not current_user:
            flash("You must be logged in to leave a review.")
            conn.close()
            return redirect(url_for('login'))

        comment = request.form['comment']
        conn.execute(
            "INSERT INTO reviews (product_id, author_name, comment) VALUES (?, ?, ?)",
            (product_id, logged_in_user, comment)
        )
        conn.commit()
        flash("Your review has been submitted!")
        conn.close()
        return redirect(url_for('product_page', product_id=product_id))

    product = conn.execute(
        "SELECT * FROM products WHERE id = ?", (product_id,)
    ).fetchone()

    reviews = conn.execute(
        "SELECT * FROM reviews WHERE product_id = ?", (product_id,)
    ).fetchall()
    conn.close()

    if not product:
        flash("Product not found.")
        return redirect(url_for('home'))

    edit_delete_links = Markup("")
    if current_user:
        if current_user['is_admin'] or (current_user['username'] == product['seller_name']):
            edit_delete_links = Markup(
                "<p><a href='{}'>Edit Product</a> | <a href='{}'>Delete Product</a></p>"
            ).format(
                url_for('edit_product', product_id=product['id']),
                url_for('delete_product', product_id=product['id'])
            )

    page = Markup(
        "<!DOCTYPE html><html><body>"
        "<h1>{}</h1>"
        "<p><strong>Price:</strong> £{}</p>"
        "<p><strong>Seller:</strong> {}</p>"
        "<p>{}</p>{}<hr><h2>Reviews</h2>"
    ).format(
        escape(product['name']),
        escape(str(product['price'])),
        escape(product['seller_name']),
        escape(product['description']),
        edit_delete_links
    )

    if reviews:
        for review in reviews:
            page += Markup("<p><strong>{}:</strong> {}</p>").format(
                escape(review['author_name']),
                escape(review['comment'])
            )
    else:
        page += Markup("<p>No reviews yet.</p>")

    if logged_in_user:
        page += Markup(
            "<h3>Leave a Review</h3>"
            "<form method='post'>"
            "<textarea name='comment' required></textarea><br>"
            "<button type='submit'>Submit Review</button>"
            "</form>"
        )

    page += Markup("<br><a href='/'>Back to Home</a></body></html>")
    return page

@app.route('/admin')
def admin_panel():
    logged_in_user = session.get('username')
    if not logged_in_user:
        flash("You must be logged in to view this page.")
        return redirect(url_for('login'))

    conn = get_db_connection()
    user = conn.execute(
        "SELECT * FROM users WHERE username = ?", (logged_in_user,)
    ).fetchone()

    if not user or not user['is_admin']:
        flash("You are not authorised to view this page.")
        conn.close()
        return redirect(url_for('home'))

    users = conn.execute('SELECT id, username FROM users').fetchall()
    products = conn.execute('SELECT id, name FROM products').fetchall()
    conn.close()

    page = Markup(
        "<!DOCTYPE html><html><head><title>Admin Panel</title></head><body>"
        "<h1>Admin Panel - Welcome, {}</h1>"
        "<h2>Users</h2><ul>"
    ).format(escape(user['username']))

    for u in users:
        page += Markup("<li>{}</li>").format(escape(u['username']))

    page += Markup("</ul><h2>All Products</h2><ul>")

    for p in products:
        page += Markup("<li>{} <a href='{}'>[Delete]</a></li>").format(
            escape(p['name']),
            url_for('delete_product', product_id=p['id'])
        )

    page += Markup("</ul><br><a href='/'>Back to Home</a></body></html>")
    return page

if __name__ == '__main__':
    app.run(debug=False)
