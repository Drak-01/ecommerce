from app.models import Category, Product
from app.models import db

class CategoryController:
    
    @staticmethod
    def get_category_by_id(category_id):
        return db.session.get(Category, category_id)

    @staticmethod
    def get_all_category(page,per_page=10):
        return (Category.query
                .order_by(Category.created_at.desc())
                .paginate(
                    page=page,
                    per_page=per_page,
                    error_out=False
                )
                )
    
    @staticmethod
    def get_category_by_name(category_name):
        return (Category.query
                        .filter_by(name=category_name)
                        .first())
        
    @staticmethod
    def add(name):
        category = Category(
            name=name
        )
        
        db.session.add(category)
        db.session.commit()
        return True 

    @staticmethod
    def delete(id):
        category = Category.query.get_or_404(id)
        db.session.delete(category)
        db.session.commit()
        
        