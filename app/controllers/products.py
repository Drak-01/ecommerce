from werkzeug.utils import secure_filename
import os
from flask import current_app, request, redirect, url_for
from app import db
from app.models import Product, OrderItem

class ProductController:
    
    @staticmethod
    def create_product(form_data, image_file=None):
        try:
            product = Product(
                name=form_data['name'],
                price=form_data['price'],
                description=form_data.get('description', ''),
                stock=form_data['stock'],
                image=ProductController._handle_image_upload(image_file)
            )
            
            db.session.add(product)
            db.session.commit()
            return product
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error creating product: {str(e)}")
            raise e
    
    def _handle_image_upload(file):
        if file and file.filename != '':
            if file.mimetype.startswith("image/"):
                filename = secure_filename(file.filename)
                upload_dir = os.path.join(current_app.root_path, 'static', 'uploads', 'products')
                os.makedirs(upload_dir, exist_ok=True)
                filepath = os.path.join(upload_dir, filename)
                file.save(filepath)
                return filename
        return None


    
    @staticmethod
    def get_all_products(page=1, per_page=10):
        return Product.query.order_by(Product.created_at.desc()).paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
    
    @staticmethod
    def get_product_by_id(product_id):
        return Product.query.get_or_404(product_id)
    
        
    @property
    def image_url(self):
        if self.image:
            image_path = os.path.join(current_app.root_path, 'static', 'uploads', 'products', self.image)
            if os.path.exists(image_path):
                return f"/static/uploads/products/{self.image}"
        return url_for('static', filename='img/no-image.png')
    
    @staticmethod
    def edit_product(product_id,form_data, image_file = None):
        try:
            product = Product.query.get(product_id)
            if not product:
                return False
            
            product.name = form_data['name']
            product.price = form_data["price"]
            product.description = form_data["description"]
            product.stock = form_data["stock"]
            
            if image_file:
                image_path = ProductController._handle_image_upload(image_file)
                if image_path:
                    product.image = image_path
            
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            return False
    
    @staticmethod
    def delete_product(product_id):
        try:
            product = Product.query.get(product_id)
            if not product:
                return False
            db.session.delete(product)
            db.session.commit()
            return True
            
        except Exception as e:
            raise e
        
        
    
    @staticmethod
    def get_similar_products(product, category_id, limit=4):
        return Product.query.filter(
            Product.id != product.id,
            Product.category_id == category_id  
        ).limit(limit).all()
    
    @staticmethod
    def get_by_categorie(id):
        return (
            Product.query.filter_by(category_id=id).first()
        )
        
    @staticmethod
    def search_products(data):
        return  Product.query.filter(
            (Product.name.ilike(f'%{data}%')) | 
            (Product.description.ilike(f'%{data}%'))
            ).all()
        
    @staticmethod
    def searchByCategori(keyword):
        results = Product.query.join(Product.category).filter(
            or_(
                Product.name.ilike(f'%{keyword}%'),
                Product.description.ilike(f'%{keyword}%'),
                Product.category.has(Category.name.ilike(f'%{keyword}%'))
            )
        ).all()