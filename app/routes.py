from flask import Blueprint, render_template, request, flash, redirect, url_for, abort
from .models import db
from flask_login import login_required, current_user
from app.controllers.products import ProductController
from app.controllers.orderController import OrderController
from app.controllers.UserController import UserController
from app.forms import ProductForm

main_routes = Blueprint("main", __name__)
admin_bp = Blueprint("admin", __name__, url_prefix='/admin')


@admin_bp.route('/')
#@login_required
def dashboard():
    return render_template("admin/index.html")

# +++++++++++++++++++++++++++++++++++++++ Routes pour product
@admin_bp.route('/products', methods=["GET"])
#@login_required
def product_list():
    page = request.args.get("page", 1, type=int)
    return render_template("admin/products.html", products=ProductController.get_all_products(page=page))

@admin_bp.route('/products/add_product', methods=["GET", "POST"])
#@login_required
def add_product():
    form = ProductForm()
    if form.validate_on_submit():
        try:
            product = ProductController.create_product(
                form_data={
                    'name': form.name.data,
                    'price': float(form.price.data),
                    'description': form.description.data,
                    'stock': int(form.stock.data)
                },
                image_file=form.image.data if form.image.data else None
            )
            flash("Produit ajouté avec succès!", "success")
            return redirect(url_for('admin.product_list'))
        
        except Exception as e:
            flash(f"Erreur: {str(e)}", "danger")
            
    return render_template('admin/add_product.html', form=form)

@admin_bp.route("/products/<int:product_id>")
#@login_required
def product_detail(product_id):
    product = ProductController.get_product_by_id(product_id)
    return render_template("admin/product_detail.html", product=product)

@admin_bp.route("/products/edit/<int:product_id>", methods=["GET","POST"])
#@login_required
def edit_product(product_id):
    product = ProductController.get_product_by_id(product_id)
    
    if not product:
        abort(404)
    
    form = ProductForm(obj=product) 
    
    if request.method == "POST" and form.validate_on_submit():
        success = ProductController.edit_prodcut(
            product_id,
            form_data={
                'name': form.name.data,
                'price': float(form.price.data),
                'description': form.description.data,
                'stock': int(form.stock.data)
            },
            image_file=form.image.data if form.image.data else None
        )
        if success: 
            flash("Produit modifier avec succès!", "success")
        else:
            flash("Erreur lors de la modification", "error")
        return redirect(url_for('admin.product_list'))
            
    else:
        return render_template(
            "admin/edit_product.html",
            product=product,
            form=form 
        )
    
@admin_bp.route("/products/delete/<int:product_id>", methods=["POST"])
#@login_required
def delete_product(product_id):
    success = ProductController.delete_product(product_id)
    if success :
        flash("Product supprimer avec succès", "success")
    else :
        flash("Erreur de suppression", "error")
    return redirect(url_for('admin.product_list'))

# ++++++++++++++++++++++++++++++++++ Routes pour commande
@admin_bp.route("/orders", methods=["GET"])
#@login_required
def list_order():
    page = request.args.get("page", 1, type=int)
    return render_template("admin/order.html", orders=OrderController.get_all_Order(page=page))

# ++++++++++++++++++++++++++++++++++ Routes pour Utilisateurs
@admin_bp.route("/users", methods=["GET"])
#@login_required
def list_user():
    page = request.args.get("page", 1, type=int)
    return render_template("admin/users.html", users=UserController.get_all_user(page=page))

# +++++++++++++++++++++++++ Interface Client


@main_routes.route('/')
def home():
    page = request.args.get("page", 1, type=int)     
    return render_template("list_product.html", products=ProductController.get_all_products(page=page))

