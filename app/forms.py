# app/forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, DecimalField, TextAreaField, IntegerField, SubmitField, PasswordField, BooleanField, SelectField
from wtforms.validators import DataRequired, NumberRange, Email, Length, EqualTo
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
    category = SelectField('Catégorie', coerce=int)
    
    submit = SubmitField('Enregistrer')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Mot de passe', validators=[DataRequired()])
    remember = BooleanField('Se souvenir de moi')
    submit = SubmitField('Se connecter')
    
class RegistrationForm(FlaskForm):
    username = StringField('Nom utilisateur', validators=[DataRequired(), Length(min=3, max=30)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Mot de passe',validators=[DataRequired(),Length(min=8)]) 
    confirm_password = PasswordField('Confirmer mot de passe',validators=[DataRequired(),EqualTo('password')])
    submit = SubmitField("S'inscrire")
    
class CategoryForm (FlaskForm):
    name = StringField("Catégories", validators=[DataRequired(), Length(min=3)])
    submit = SubmitField("Enregistrer")