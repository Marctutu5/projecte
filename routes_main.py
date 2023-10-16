from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from werkzeug.utils import secure_filename
import os
from models import db, products, categories

routes_main = Blueprint('routes_main', __name__)

UPLOAD_FOLDER = 'static/images'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Rutas
@routes_main.route('/products/list/', methods=['GET', 'POST'])
def mostrar_productos():
    category_slug = request.args.get('category') if request.method == 'GET' else None

    if category_slug:
        productos = products.query.join(categories).filter(categories.slug == category_slug).all()
    else:
        productos = products.query.all()
    category_list = categories.query.all()

    return render_template("/products/list.html", productos=productos, categories=category_list)


def validate_product(updating=False):
    errors = []

    title = request.form.get('title')
    if not title:
        errors.append("El título no puede estar vacío.")
    elif len(title) > 255:
        errors.append("El título no puede superar los 255 caracteres.")

    description = request.form.get('description')
    if not description:
        errors.append("La descripción no puede estar vacía.")

    try:
        price = float(request.form.get('price'))
        if not price:
            errors.append("El precio no puede estar vacío.")
    except ValueError:
        errors.append("El precio debe ser un número.")

    image = request.files.get('image')
    if not updating:
        if not image or not image.filename:
            errors.append("La foto no puede estar vacía.")
        elif image and image.content_length > (2 * 1024 * 1024):
            errors.append("El archivo no puede superar los 2MB.")
    else:
        if image and image.content_length > (2 * 1024 * 1024):
            errors.append("El archivo no puede superar los 2MB.")

    category_id = request.form.get('category')
    if not category_id:
        errors.append("Debes seleccionar una categoría.")

    return errors

@routes_main.route('/products/create/', methods=['GET', 'POST'])
def create_product():
    category_list = categories.query.all()
    
    if request.method == 'POST':
        errors = validate_product()
        
        if errors:
            for error in errors:
                flash(error, 'danger')
            return render_template('products/create.html', categories=category_list)
        
        title = request.form.get('title')
        description = request.form.get('description')
        price = float(request.form.get('price'))
        category_id = request.form.get('category')

        image = request.files.get('image')
        filename = None
        if allowed_file(image.filename):
            filename = secure_filename(image.filename)
            image.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))

        try:
            product = products(
                title=title,
                description=description,
                price=price,
                category_id=category_id,
                photo=filename
            )
            db.session.add(product)
            db.session.commit()
            flash("Producto creado con éxito", "success")
            return redirect(url_for('routes_main.mostrar_productos'))
        except Exception as e:
            flash(f"Error al crear el producto: {e}", "danger")
            return render_template('products/create.html', categories=category_list)

    return render_template('products/create.html', categories=category_list)

@routes_main.route('/products/update/<int:product_id>/', methods=['GET', 'POST'])
def update_product(product_id):
    product = products.query.get(product_id)
    category_list = categories.query.all()

    if request.method == 'POST':
        errors = validate_product(updating=True)
        
        if errors:
            for error in errors:
                flash(error, 'danger')
            return render_template('products/update.html', product=product, categories=category_list)
        
        title = request.form.get('title')
        description = request.form.get('description')
        price = float(request.form.get('price'))
        category_id = request.form.get('category')

        image = request.files.get('image')
        if not image or not image.filename:
            image_path = product.photo
        else:
            if allowed_file(image.filename):
                filename = secure_filename(image.filename)
                image.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
                image_path = filename

        try:
            product.title = title
            product.description = description
            product.price = price
            product.category_id = category_id
            product.photo = image_path
            db.session.commit()
            flash("Producto actualizado con éxito", "success")
            return redirect(url_for('routes_main.mostrar_productos'))
        except Exception as e:
            flash(f"Error al actualizar el producto: {e}", "danger")
            return render_template('products/update.html', product=product, categories=category_list)

    return render_template('products/update.html', product=product, categories=category_list)


@routes_main.route('/products/delete/<int:product_id>', methods=['GET', 'POST'])
def delete_product(product_id):
    try:
        product = products.query.get(product_id)
        db.session.delete(product)
        db.session.commit()
        flash("Producto eliminado con éxito", "success")
    except Exception as e:
        flash(f"Error al eliminar el producto: {e}", "danger")
        
    return redirect(url_for('routes_main.mostrar_productos'))