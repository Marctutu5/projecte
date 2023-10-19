from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from werkzeug.utils import secure_filename
import os
from .models import db, products, categories
from .forms import ProductForm

routes_main = Blueprint('routes_main', __name__)

UPLOAD_FOLDER = 'static/images'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@routes_main.route('/products/list/', methods=['GET', 'POST'])
def mostrar_productos():
    category_slug = request.args.get('category') if request.method == 'GET' else None

    if category_slug:
        if category_slug == 'TODOS':
            # Si se selecciona "TODOS", muestra todos los productos
            productos = products.query.all()
        else:
            # Filtra los productos por la categoría seleccionada
            productos = products.query.join(categories).filter(categories.slug == category_slug).all()
    else:
        # Si no se proporciona una categoría, muestra todos los productos
        productos = products.query.all()

    category_list = categories.query.all()

    # Crear una instancia del formulario aquí y pasarlo al contexto
    form = ProductForm()
    form.category.choices = [(cat.id, cat.name) for cat in categories.query.all()]

    # Configurar el valor predeterminado del campo 'category' si se proporciona una categoría actual
    if category_slug:
        form.category.default = category_slug
        form.process()

    return render_template("/products/list.html", productos=productos, categories=category_list, form=form)

@routes_main.route('/products/create/', methods=['GET', 'POST'])
def create_product():
    form = ProductForm()
    form.category.choices = [(cat.id, cat.name) for cat in categories.query.all()]

    if form.validate_on_submit():
        image = form.image.data
        filename = None
        if image and allowed_file(image.filename):
            filename = secure_filename(image.filename)
            image.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))

        product = products(
            title=form.title.data,
            description=form.description.data,
            price=form.price.data,
            category_id=form.category.data,
            photo=filename
        )
        db.session.add(product)
        db.session.commit()
        flash("Producto creado con éxito", "success")
        return redirect(url_for('routes_main.mostrar_productos'))

    return render_template('products/create.html', form=form)

@routes_main.route('/products/update/<int:product_id>', methods=['POST', 'GET'])
def update_product(product_id):
    product = products.query.get(product_id)

    if not product:
        flash("Producto no encontrado", "danger")
        return redirect(url_for('routes_main.mostrar_productos'))

    form = ProductForm(obj=product)
    form.category.choices = [(cat.id, cat.name) for cat in categories.query.all()]

    if form.validate_on_submit():
        if (
            product.title != form.title.data or
            product.description != form.description.data or
            product.price != form.price.data or
            product.category_id != form.category.data
        ):
            product.title = form.title.data
            product.description = form.description.data
            product.price = form.price.data
            product.category_id = form.category.data

            new_image = form.image.data
            if new_image and allowed_file(new_image.filename):
                filename = secure_filename(new_image.filename)
                new_image.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
                product.photo = filename

            db.session.commit()
            flash("Producto actualizado con éxito", "success")

        return redirect(url_for('routes_main.mostrar_productos'))
    else:
        return render_template('products/update.html', form=form, product=product)

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


@routes_main.route('/products/read/<int:product_id>', methods=['GET'])
def read_product(product_id):
    product = products.query.get(product_id)

    if not product:
        flash("Producto no encontrado", "danger")
        return redirect(url_for('routes_main.mostrar_productos'))

    return render_template('products/read.html', product=product)

