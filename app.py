from flask import Flask, render_template, g, request, redirect, url_for, flash
import sqlite3
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
DATABASE = 'db/database.db'
UPLOAD_FOLDER = 'static/images'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = "muydificil"

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.route('/products/list/', methods=['GET', 'POST'])
def mostrar_productos():
    cur = get_db().cursor()
    
    category_slug = request.args.get('category') if request.method == 'GET' else None

    if category_slug:
        cur.execute("SELECT * FROM products JOIN categories ON products.category_id = categories.id WHERE categories.slug = ?", (category_slug,))
    else:
        cur.execute("SELECT * FROM products")
        
    productos = cur.fetchall()
    
    cur.execute("SELECT * FROM categories")
    categories = cur.fetchall()

    return render_template("/products/list.html", productos=productos, categories=categories)


@app.route('/products/create/', methods=['GET', 'POST'])
def create_product():
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        price = request.form.get('price')
        category_id = request.form.get('category')
        image = request.files['image']

        if 'image' not in request.files:
            flash('No image part', 'danger')
            return redirect(request.url)
        if image.filename == '':
            flash('No selected image', 'danger')
            return redirect(request.url)

        filename = None
        if image and allowed_file(image.filename):
            filename = secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        try:
            cur = get_db().cursor()
            cur.execute("""
                INSERT INTO products (title, description, price, category_id, photo, created, updated)
                VALUES (?, ?, ?, ?, ?, DATETIME('now'), DATETIME('now'))
            """, (title, description, price, category_id, filename))
            get_db().commit()

            flash("Producto creado con éxito", "success")
            return redirect(url_for('mostrar_productos'))
        except Exception as e:
            flash(f"Error al crear el producto: {e}", "danger")
            return redirect(url_for('create_product'))

    # Para mostrar las categorías disponibles:
    cur = get_db().cursor()
    cur.execute("SELECT * FROM categories")
    categories = cur.fetchall()
    return render_template('products/create.html', categories=categories)


@app.route('/products/update/<int:product_id>/', methods=['GET', 'POST'])
def update_product(product_id):
    cur = get_db().cursor()

    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        price = request.form.get('price')
        category_id = request.form.get('category')
        image = request.files.get('image')

        update_values = [title, description, price, category_id]
        update_query = """
            UPDATE products
            SET title=?, description=?, price=?, category_id=?, updated=DATETIME('now')
        """

        # Si se ha proporcionado una nueva imagen, la procesamos
        if image and image.filename:
            if not allowed_file(image.filename):
                flash("Tipo de archivo no permitido", "danger")
                return redirect(request.url)

            filename = secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            # Agregamos la imagen al query de actualización
            update_query += ", photo=? "
            update_values.append(filename)

        update_query += " WHERE id=?"
        update_values.append(product_id)

        try:
            cur.execute(update_query, tuple(update_values))
            get_db().commit()

            flash("Producto actualizado con éxito", "success")
            return redirect(url_for('mostrar_productos'))

        except Exception as e:
            flash(f"Error al actualizar el producto: {e}", "danger")
            return redirect(url_for('update_product', product_id=product_id))

    # Obtener información del producto para mostrarla en el formulario
    cur.execute("SELECT * FROM products WHERE id=?", (product_id,))
    product = cur.fetchone()

    # Para mostrar las categorías disponibles:
    cur.execute("SELECT * FROM categories")
    categories = cur.fetchall()
    
    return render_template('products/update.html', product=product, categories=categories)



if __name__ == '__main__':
    app.run(debug=True)

