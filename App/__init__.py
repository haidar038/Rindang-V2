import io, os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_admin import Admin
from flask_socketio import SocketIO
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
from werkzeug.security import generate_password_hash
from flask_toastr import Toastr
from dotenv import load_dotenv

app = Flask(__name__)

socketio = SocketIO(cors_allowed_origins="*")
db = SQLAlchemy()
login_manager = LoginManager()
toastr = Toastr()
jwt = JWTManager()
admin = Admin(name='admin')
buffer = io.BytesIO()
migrate = Migrate(app, db)
load_dotenv()

UPLOAD_FOLDER = 'App/static/uploads/profile_pics'  # Sesuaikan path folder upload
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def create_app():
    app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY", 'rindang_digifarm') # Gunakan variabel environment atau nilai default
    app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{os.environ.get("MYSQLUSER")}:{os.environ.get("MYSQLPASSWORD")}@{os.environ.get("MYSQLHOST")}:{os.environ.get("MYSQLPORT")}/{os.environ.get("MYSQLDATABASE")}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        "pool_pre_ping": True, 
        "pool_recycle": 300,
    }
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Batasi ukuran file (misal: 16MB)

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