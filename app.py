from flask import Flask, render_template, g, request, redirect, url_for, flash
import sqlite3
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Configuración
DATABASE = 'db/database.db'
UPLOAD_FOLDER = 'static/images'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
SECRET_KEY = "muydificil"

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = SECRET_KEY

# Funciones

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

def close_db(e=None):
    db = g.pop('_database', None)
    if db is not None:
        db.close()

def get_categories(cur):
    cur.execute("SELECT * FROM categories")
    return cur.fetchall()

@app.teardown_appcontext
def teardown_db(exception):
    close_db(exception)

# Rutas

@app.route('/products/list/', methods=['GET', 'POST'])
def mostrar_productos():
    cur = get_db().cursor()
    category_slug = request.args.get('category') if request.method == 'GET' else None

    if category_slug:
        cur.execute("SELECT * FROM products JOIN categories ON products.category_id = categories.id WHERE categories.slug = ?", (category_slug,))
    else:
        cur.execute("SELECT * FROM products")
        
    productos = cur.fetchall()
    categories = get_categories(cur)
    cur.close()

    return render_template("/products/list.html", productos=productos, categories=categories)

def validate_product(updating=False):
    errors = []

    title = request.form.get('title')
    if not title:
        errors.append("El títol no pot estar buit.")
    elif len(title) > 255:
        errors.append("El títol no pot superar els 255 caràcters.")

    description = request.form.get('description')
    if not description:
        errors.append("La descripció no pot estar buit.")

    try:
        price = float(request.form.get('price'))
        if not price:
            errors.append("El preu no pot estar buit.")
    except ValueError:
        errors.append("El preu ha de ser un número.")

    image = request.files.get('image')
    if not updating:
        if not image or not image.filename:
            errors.append("La foto no pot estar buit.")
        elif image and image.content_length > (2 * 1024 * 1024):
            errors.append("El fitxer no pot superar els 2MB.")
    else:
        if image and image.content_length > (2 * 1024 * 1024):
            errors.append("El fitxer no pot superar els 2MB.")

    category_id = request.form.get('category')
    if not category_id:
        errors.append("Cal seleccionar una categoria.")

    return errors

@app.route('/products/create/', methods=['GET', 'POST'])
def create_product():
    cur = get_db().cursor()
    categories = get_categories(cur)
    
    if request.method == 'POST':
        errors = validate_product()
        
        if errors:
            for error in errors:
                flash(error, 'danger')
            return render_template('products/create.html', categories=categories)
        
        title = request.form.get('title')
        description = request.form.get('description')
        price = float(request.form.get('price'))
        category_id = request.form.get('category')

        image = request.files.get('image')
        filename = None
        if allowed_file(image.filename):
            filename = secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        try:
            cur.execute("""
                INSERT INTO products (title, description, price, category_id, photo, created, updated)
                VALUES (?, ?, ?, ?, ?, DATETIME('now'), DATETIME('now'))
            """, (title, description, price, category_id, filename))
            get_db().commit()
            flash("Producte creat amb èxit", "success")
            return redirect(url_for('mostrar_productos'))
        except sqlite3.Error as e:
            flash(f"Error al crear el producte: {e}", "danger")
            return render_template('products/create.html', categories=categories)

    return render_template('products/create.html', categories=categories)

@app.route('/products/update/<int:product_id>/', methods=['GET', 'POST'])
def update_product(product_id):
    cur = get_db().cursor()

    if request.method == 'POST':
        errors = validate_product(updating=True)
        
        if errors:
            for error in errors:
                flash(error, 'danger')
            product = cur.execute("SELECT * FROM products WHERE id=?", (product_id,)).fetchone()
            categories = get_categories(cur)
            return render_template('products/update.html', product=product, categories=categories)
        
        title = request.form.get('title')
        description = request.form.get('description')
        price = float(request.form.get('price'))
        category_id = request.form.get('category')

        image = request.files.get('image')
        if not image or not image.filename:
            image_path = cur.execute("SELECT photo FROM products WHERE id=?", (product_id,)).fetchone()[0]
        else:
            if allowed_file(image.filename):
                filename = secure_filename(image.filename)
                image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                image_path = filename

        try:
            cur.execute("""
                UPDATE products
                SET title=?, description=?, price=?, category_id=?, photo=?, updated=DATETIME('now')
                WHERE id=?
            """, (title, description, price, category_id, image_path, product_id))
            get_db().commit()
            flash("Producte actualitzat amb èxit", "success")
            return redirect(url_for('mostrar_productos'))
        except sqlite3.Error as e:
            flash(f"Error al actualitzar el producte: {e}", "danger")
            product = cur.execute("SELECT * FROM products WHERE id=?", (product_id,)).fetchone()
            categories = get_categories(cur)
            return render_template('products/update.html', product=product, categories=categories)

    product = cur.execute("SELECT * FROM products WHERE id=?", (product_id,)).fetchone()
    categories = get_categories(cur)
    return render_template('products/update.html', product=product, categories=categories)

@app.route('/products/delete/<int:product_id>', methods=['GET', 'POST'])
def delete_product(product_id):
    cur = get_db().cursor()

    try:
        cur.execute("DELETE FROM products WHERE id=?", (product_id,))
        get_db().commit()
        flash("Producte esborrat amb èxit", "success")
    except sqlite3.Error as e:
        flash(f"Error al esborrar el producte: {e}", "danger")
        
    return redirect(url_for('mostrar_productos'))

if __name__ == '__main__':
    app.run()


