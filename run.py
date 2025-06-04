from app import create_app
from app.models import db
from flask_migrate import Migrate

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)