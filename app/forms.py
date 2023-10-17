from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, DecimalField, SelectField, FileField, SubmitField, PasswordField
from wtforms.validators import DataRequired, Email

class ProductForm(FlaskForm):
    title = StringField('Título', validators=[DataRequired()])
    description = TextAreaField('Descripción', validators=[DataRequired()])
    price = DecimalField('Precio', validators=[DataRequired()])
    category = SelectField('Categoría', coerce=int, validators=[DataRequired()])
    image = FileField('Imagen', validators=[])
    submit = SubmitField('Guardar')

class CategoryForm(FlaskForm):
    name = StringField('Nombre', validators=[DataRequired()])
    slug = StringField('Slug', validators=[DataRequired()])
    submit = SubmitField('Guardar')

class UserRegistrationForm(FlaskForm):
    name = StringField('Nombre', validators=[DataRequired()])
    email = StringField('Correo electrónico', validators=[DataRequired(), Email()])
    password = PasswordField('Contraseña', validators=[DataRequired()])
    submit = SubmitField('Registrarse')

class LoginForm(FlaskForm):
    email = StringField('Correo electrónico', validators=[DataRequired(), Email()])
    password = PasswordField('Contraseña', validators=[DataRequired()])
    submit = SubmitField('Iniciar sesión')