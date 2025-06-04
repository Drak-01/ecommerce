Il faut installer flask.
  1. Créer un environnement virtuel python
     python3 -m venv .venv
     source .venv/bin/activate
  2. installation
     pip install flask
     pip install flask flask_sqlalchemy flask_migrate
  3. après avoir configurer le projet il faut mettre a jour la base de données
     flask db init       
     flask db migrate -m "Initial migration"
     flask db upgrade
     LANCE LE PROJET
       python3 run.py 
     
