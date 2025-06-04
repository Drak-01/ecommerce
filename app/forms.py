# app/forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, DecimalField, TextAreaField, IntegerField, SubmitField
from wtforms.validators import DataRequired, NumberRange
from flask_wtf.file import FileField, FileAllowed

class ProductForm(FlaskForm):
    name = StringField('Nom du produit', validators=[
        DataRequired(message="Le nom est obligatoire")
    ])
    
    price = DecimalField('Prix', places=2, validators=[
        DataRequired(message="Le prix est obligatoire"),
        NumberRange(min=0.01, message="Le prix doit être positif")
    ])
    
    description = TextAreaField('Description')
    
    stock = IntegerField('Stock', validators=[
        DataRequired(message="Le stock est obligatoire"),
        NumberRange(min=0, message="Le stock ne peut pas être négatif")
    ])
    
    image = FileField('Image du produit', validators=[
        FileAllowed(['jpg', 'png', 'jpeg'], 'Seules les images JPG/PNG sont autorisées')
    ])
    
    submit = SubmitField('Enregistrer')