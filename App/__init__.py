import io, os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_admin import Admin
from flask_socketio import SocketIO
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
from werkzeug.security import generate_password_hash
from flask_toastr import Toastr
from dotenv import load_dotenv

socketio = SocketIO(cors_allowed_origins="*")
db = SQLAlchemy()
login_manager = LoginManager()
toastr = Toastr()
jwt = JWTManager()
admin = Admin(name='admin')
buffer = io.BytesIO()
load_dotenv()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY", 'rindang_digifarm') # Gunakan variabel environment atau nilai default
    app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql://{os.environ.get("MYSQLUSER")}:{os.environ.get("MYSQLPASSWORD")}@{os.environ.get("MYSQLHOST")}:{os.environ.get("MYSQLPORT")}/{os.environ.get("MYSQLDATABASE")}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    socketio.init_app(app)
    login_manager.init_app(app)
    toastr.init_app(app)
    jwt.init_app(app)

    from .auth.routes import auth
    from .views.routes import views
    from .admin.routes import admin_page

    app.register_blueprint(auth, url_prefix='/')
    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(admin_page, url_prefix='/')

    login_manager.login_view = 'auth.login'

    from .models import AppAdmin

    with app.app_context():
        db.create_all()

        if not AppAdmin.query.first():
            supersu = AppAdmin(username='admin', password=generate_password_hash('admrindang123', method='pbkdf2'))
            db.session.add(supersu)
            db.session.commit()

    return app