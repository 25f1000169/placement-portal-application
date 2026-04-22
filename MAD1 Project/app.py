from flask import Flask
app = None
from application.database import db
def create_app():
    app = Flask(__name__)
    # app.debug = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mad1_project.sqlite3'
    app.secret_key = 'mad1_project_secret_key'  
    db.init_app(app)
    app.app_context().push()
    return app

app = create_app()
from application.controllers import *
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        admin_exists = Admin.query.filter_by(username="admin").first()
        if not admin_exists:
            admin = Admin(username="admin", pwd="admin123")
            db.session.add(admin)
            db.session.commit()
        app.run()
