from flask import Blueprint, current_app, render_template, request, flash, redirect, url_for, abort, jsonify
from .models import Category, OrderItem, Orders, Product, User, db
from flask_login import login_required, current_user, logout_user
from app.controllers.products import ProductController
from app.controllers.orderController import OrderController
from app.controllers.UserController import UserController
from app.controllers.categoryController import CategoryController
from app.forms import *
from functools import wraps
import logging
from werkzeug.exceptions import BadRequest

main_routes = Blueprint("main", __name__)
admin_bp = Blueprint("admin", __name__, url_prefix='/admin')

logger = logging.getLogger(__name__)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Authentification requise', 'warning')
            return redirect(url_for('admin.login_admin', next=request.url))
            
        if not getattr(current_user, 'is_admin', False):
            logger.warning(f'Tentative d\'accès non autorisé par l\'utilisateur {current_user.id}')
            abort(403)
            
        return f(*args, **kwargs)
    return decorated_function

# ==================== ADMIN ROUTES ====================
@admin_bp.route("/login", methods=["GET", "POST"])
def login_admin():
    """Route de connexion admin sécurisée"""
    if current_user.is_authenticated and getattr(current_user, 'is_admin', False):
        return redirect(url_for('admin.dashboard'))
        
    form = LoginForm()
    
    if form.validate_on_submit():
        success, user = UserController.login_admin(form)
        if success:
            next_page = request.args.get('next', url_for('admin.dashboard'))
            return redirect(next_page)
            
    return render_template("admin/auth/login.html", form=form)

@admin_bp.route('/logout')
@login_required
@admin_required
def logout():
    """Déconnexion sécurisée"""
    logout_user()
    flash('Vous avez été déconnecté', 'success')
    return redirect(url_for('admin.login_admin'))

@admin_bp.route('/')
@login_required
@admin_required
def dashboard():
    nb_orders = OrderController.order_count()
    nb_users = UserController.user_count()
    return render_template("admin/index.html", nb_orders=nb_orders, nb_users=nb_users)

@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard1():
    # 1. Statistiques de base
    stats = {
        'product_count': Product.query.count(),
        'order_count': Orders.query.count(),
        'user_count': User.query.count(),
        'total_revenue': db.session.query(db.func.sum(Orders.total)).scalar() or 0
    }

    # 2. Commandes récentes
    recent_orders = (Orders.query
                    .order_by(Orders.created_at.desc())
                    .limit(5)
                    .all())

    # 3. Produits en faible stock
    low_stock_products = (Product.query
                         .filter(Product.stock < 20)
                         .order_by(Product.stock.asc())
                         .limit(5)
                         .all())

    # 4. Produits les plus vendus
    top_products = (db.session.query(
                        Product.id,
                        Product.name,
                        Product.price,
                        Product.image,
                        db.func.sum(OrderItem.quantity).label('total_ordered')
                    )
                    .join(OrderItem, Product.id == OrderItem.product_id)
                    .group_by(Product.id)
                    .order_by(db.desc('total_ordered'))
                    .limit(5)
                    .all())
    
    max_ordered = max([product.total_ordered for product in top_products]) if top_products else 1

    # 5. Statistiques mensuelles (version compatible MySQL)
    monthly_stats = (db.session.query(
                        db.func.date_format(Orders.created_at, '%Y-%m').label('month'),
                        db.func.count(Orders.id).label('order_count'),
                        db.func.sum(Orders.total).label('total_revenue')
                    )
                    .group_by('month')
                    .order_by(db.desc('month'))
                    .limit(6)
                    .all())

    return render_template('admin/dashboard.html',
                         # Statistiques de base
                         product_count=stats['product_count'],
                         order_count=stats['order_count'],
                         user_count=stats['user_count'],
                         total_revenue=stats['total_revenue'],
                         
                         # Listes
                         recent_orders=recent_orders,
                         low_stock_products=low_stock_products,
                         top_products=top_products,
                         
                         # Calculs
                         max_ordered=max_ordered,
                         monthly_stats=monthly_stats)

# ==================== ADMIN ROUTES ====================
# =======================   Routes pour les produits
@admin_bp.route('/products', methods=["GET"])
@login_required
@admin_required
def product_list():
    page = request.args.get("page", 1, type=int)
    products = ProductController.get_all_products(page=page)
    return render_template("admin/products.html", products=products)

@admin_bp.route('/products/add_product', methods=["GET", "POST"])
@login_required
@admin_required
def add_product():
    form = ProductForm()
    
    categories = Category.query.order_by(Category.name).all()
    form.category.choices = [(c.id, c.name) for c in categories]
    
    if form.validate_on_submit():
        try:
            category = Category.query.get(form.category.data)
            if not category:
                flash("Catégorie invalide", "danger")
                return redirect(url_for('admin.add_product'))
            
            product = ProductController.create_product(
                form_data={
                    'name': form.name.data,
                    'price': float(form.price.data),
                    'description': form.description.data,
                    'stock': int(form.stock.data),
                    'category_id': int(form.category.data)  
                },
                image_file=form.image.data
            )
            
            flash("Produit ajouté avec succès!", "success")
            return redirect(url_for('admin.product_list'))
            
        except ValueError as e:
            flash(f"Erreur de validation: {str(e)}", "danger")
        except Exception as e:
            flash(f"Erreur lors de l'ajout: {str(e)}", "danger")
            current_app.logger.error(f"Erreur add_product: {str(e)}")
    
    return render_template('admin/add_product.html', form=form, categories=categories)

@admin_bp.route("/products/<int:product_id>")
@login_required
@admin_required
def product_detail(product_id):
    product = ProductController.get_product_by_id(product_id)
    if not product:
        abort(404)
    return render_template("admin/product_detail.html", product=product)

@admin_bp.route("/products/edit/<int:product_id>", methods=["GET","POST"])
@login_required
@admin_required
def edit_product(product_id):
    
    product = ProductController.get_product_by_id(product_id)
    
    if not product:
        abort(404)
    
    form = ProductForm(obj=product)
    
    categories = Category.query.order_by(Category.name).all()
    form.category.choices = [(c.id, c.name) for c in categories]
    
    if form.validate_on_submit():
        try:
            category = Category.query.get(form.category.data)

            success = ProductController.edit_product(  # Correction du nom de méthode
                product_id,
                form_data={
                    'name': form.name.data,
                    'price': float(form.price.data),
                    'description': form.description.data,
                    'stock': int(form.stock.data),
                    'category_id': int(form.category.data)  
                },
                image_file=form.image.data
            )
            if success: 
                flash("Produit modifié avec succès!", "success")
                return redirect(url_for('admin.product_list'))
            else:
                flash("Erreur lors de la modification", "error")
        except Exception as e:
            flash(f"Erreur: {str(e)}", "error")
    
    return render_template("admin/edit_product.html", product=product, form=form, categories=categories)

@admin_bp.route("/products/delete/<int:product_id>", methods=["POST"])
@login_required
@admin_required
def delete_product(product_id):
    if ProductController.delete_product(product_id):
        flash("Produit supprimé avec succès", "success")
    else:
        flash("Erreur de suppression", "error")
    return redirect(url_for('admin.product_list'))

# =======================   Routes pour les produits utilisateurs
@main_routes.route("/products/details/<int:id>", methods=["GET"])
def product_details(id):
    product = ProductController.get_product_by_id(id)
    
    if not product:
        abort(404)
        
    products = ProductController.get_similar_products(product, product.category_id)
    
    return render_template("product_details.html", product=product, products_similaire=products)

@main_routes.route('/resultats', methods=['GET'])
def search_products():
    mot = request.args.get('q', '').strip()

    if not mot:
        flash("Veuillez fournir un mot-clé pour la recherche", "warning")
        return redirect(url_for('main.home'))

    products = ProductController.search_products(mot)

    return render_template("searchResultat.html", products=products)


@main_routes.route('/product/<int:product_id>', methods=['POST'])
@login_required
def add_prod_order(product_id):
    try:
        product = ProductController.get_product_by_id(product_id)  
        
        order = OrderController.get_order_by_userid(current_user.id) #les commandes de l'utilisateur
        
        if order and product :
            order_item = OrderController.get_order_item(product_id, order.id)
            if order_item:
                order_item.quantity += 1
                order_item.price = product.price
            else: 
                order_item = OrderItem(
                    order_id = order.id,
                    product_id = product_id,
                    quantity = 1,
                    price= product.price,
                )
                db.session.add(order_item)
            
            order.total = sum(item.quantity * item.price for item in order.items) 
        
            db.session.commit()
            return jsonify({
                'success' : True, 
                'message' : 'Produit ajouté avec succès'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error' : True, "message" : "Une erreur s\'est produite lors de l\'ajout du produit."})
      
@admin_bp.route('/user/details/<int:id>', methods=["GET"])
@login_required
@admin_required
def user_details(id):
    user = UserController.get_user_by_id(id)
    return render_template('admin/user_details.html', user=user)

@admin_bp.route("/user/details/delete/<int:id>", methods=["DELETE"])
@login_required
@admin_required
def deleteUser(id):
    try:
        success = UserController.deleteUser(id) 
        print("id: ", success)
        if success == True:
            return jsonify({
                "success" : True,
                "message" : ""
            }) 
        else :
            return jsonify({
                "success" : False,
                "message" : "Erreur de suppression user"
            })
    except Exception as e:
        raise e

# ========================= Routes pour les commandes
@admin_bp.route("/orders", methods=["GET"])
@login_required
@admin_required
def list_order():
    page = request.args.get("page", 1, type=int)
    orders = OrderController.get_all_Order(page=page)
    return render_template("admin/order.html", orders=orders)

@admin_bp.route("/order/details/<int:id>")
@login_required
@admin_required
def order_details(id):
    user = UserController.get_user_by_id(id)
    orders = OrderController.get_orders_by_user(id)
    return render_template('admin/orderdetails.html', orders=orders, user=user)


# Routes pour les utilisateurs
@admin_bp.route("/users", methods=["GET"])
@login_required
@admin_required
def list_user():
    page = request.args.get("page", 1, type=int)
    users = UserController.get_all_users(page=page)
    return render_template("admin/users.html", users=users)



# ========================= Routes pour les Category
@admin_bp.route("/category", methods=["GET"])
@admin_required
@login_required
def category():
    page = request.args.get("page", 1, type=int) 
    categories = CategoryController.get_all_category(page)
    
    return render_template("admin/category.html", categories=categories)

@admin_bp.route("/category/add", methods=["GET", "POST"])
@admin_required
@login_required
def addCategory():
    form = CategoryForm()

    if request.method == 'POST':
        if request.is_json:
            try:
                data = request.get_json()
                
                CategoryController.add(data['name'])
                return jsonify({'message': 'Category added successfully'}), 201
            except Exception as e:
                print(f"Error adding category: {str(e)}")
                return jsonify({'error': 'Failed to add category'}), 500
        else:
            if form.validate_on_submit():
                try:
                    CategoryController.add({'name': form.name.data})
                    flash('Category added successfully!', 'success')
                    return redirect(url_for('admin.category'))
                except Exception as e:
                    flash(f'Error adding category: {str(e)}', 'danger')
                    return render_template('admin/add_category.html', form=form)

    return render_template('admin/add_category.html', form=form)

@admin_bp.route("/category/delete/<int:id>", methods=['DELETE'])
@admin_required
@login_required
def deleteCategory(id):
    try:

        if request.method == "DELETE" and not ProductController.get_by_categorie(id):
            CategoryController.delete(id)
            return jsonify({"message": "Suppression avec Succès", 'success':True})

        else:
            return jsonify({"message": "Erreur de suppression", 'error':False})
        
    except Exception as e:
        raise e

# =======================   Routes pour les Commandes utilisateurs

@main_routes.route('/order', methods=["GET"])
@login_required
def orders_user():
    orders = OrderController.get_orders_by_user(current_user.id)
    
    return render_template('orders.html', orders=orders)

@main_routes.route('/order/update-item/<int:item_id>', methods=['POST'])
@login_required
def update_order_item(item_id):
    try:
        data = request.get_json()
        change = int(data.get('change', 0))
        
        if change not in (1, -1):
            return jsonify({'success': False, 'message': 'Changement invalide'}), 400
        
        item = OrderItem.query.get_or_404(item_id)
        if item.order.user_id != current_user.id:
            abort(403)
        
        new_quantity = item.quantity + change
        if new_quantity < 1:
            return jsonify({'success': False, 'message': 'Quantité minimale atteinte'}), 400
        
        item.quantity = new_quantity
        order_total = sum(i.product.price * i.quantity for i in item.order.items)
        item.order.total = order_total
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'new_quantity': new_quantity,
            'order_id': item.order.id,
            'order_total': order_total,
            'line_total': item.product.price * new_quantity
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@main_routes.route('/order/remove-item/<int:item_id>', methods=['DELETE'])
@login_required
def remove_order_item(item_id):
    try:
        item = OrderItem.query.get_or_404(item_id)
        if item.order.user_id != current_user.id:
            abort(403)
        
        order_id = item.order.id
        db.session.delete(item)
        
        order = item.order
        order.total = sum(i.product.price * i.quantity for i in order.items)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'order_id': order_id,
            'order_total': order.total
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500
    



# ==================== CLIENT ROUTES ====================
@main_routes.route('/')
def home():
    page = request.args.get("page", 1, type=int)   
    nb_orders = OrderController.order_count()
    products = ProductController.get_all_products(page=page)
    return render_template("list_product.html", products=products, nb_orders=nb_orders)

@main_routes.route('/login', methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))
    
    form = LoginForm()
    if form.validate_on_submit():
        success, user = UserController.login(form)
        if success:
            flash("Connexion réussie!", "success")
            return redirect(url_for("main.home"))
        else:
            flash("Email ou mot de passe incorrect", "danger")
    
    return render_template("auth/login.html", form=form)

@main_routes.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        try:
            if UserController.register(form):
                flash("Inscription réussie! Vous pouvez maintenant vous connecter.", "success")
                return redirect(url_for("main.login"))
        except Exception as e:
            flash(f"Erreur lors de l'inscription: {str(e)}", "danger")
    
    return render_template("auth/register.html", form=form)

@main_routes.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Déconnexion réussie.", "info")
    return redirect(url_for('main.login'))
