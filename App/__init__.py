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
from mailersend import emails
from dotenv import load_dotenv
from flask_sitemap import Sitemap
from flask_flatpages import FlatPages

app = Flask(__name__)

load_dotenv()
socketio = SocketIO(cors_allowed_origins="*")
db = SQLAlchemy()
login_manager = LoginManager()
toastr = Toastr()
jwt = JWTManager()
admin = Admin(name='admin')
buffer = io.BytesIO()
migrate = Migrate(app, db)
ext = Sitemap(app=app)
flatpages = FlatPages()
mailer = emails.NewEmail(os.getenv('MAILERSEND_API_KEY'))

UPLOAD_FOLDER = 'App/static/uploads/profile_pics'  # Sesuaikan path folder upload
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def send_email(to_email, subject, html_content):
    """Mengirim email menggunakan MailerSend.

    Args:
        to_email (str): Alamat email penerima.
        subject (str): Subjek email.
        html_content (str): Konten HTML email.
    """

    try:
        # Menggunakan API key dari environment variable
        mailer = emails.NewEmail(os.getenv('MAILERSEND_API_KEY'))

        mail_body = {}

        mail_from = {
            "name": "M. Khaidar", # Ganti dengan nama pengirim Anda
            "email": "haidar038@gmail.com"  # Ganti dengan email pengirim TERVERIFIKASI
        }

        recipients = [
            {
                "name": "Recipient Name", # Anda bisa mengambil nama pengguna jika ada
                "email": to_email,
            }
        ]

        # (Opsional) Tambahkan reply_to jika diperlukan
        # reply_to = {
        #     "name": "Nama Pengirim",
        #     "email": "reply@rindangdigifarm.com",  # Ganti dengan email yang ingin Anda gunakan untuk balasan
        # }

        mailer.set_mail_from(mail_from, mail_body)
        mailer.set_mail_to(recipients, mail_body)
        mailer.set_subject(subject, mail_body)
        mailer.set_html_content(html_content, mail_body)
        #mailer.set_plaintext_content("Ini adalah konten teks", mail_body) # Opsional: Tambahkan teks biasa jika diperlukan 
        #mailer.set_reply_to(reply_to, mail_body) # Opsional

        response = mailer.send(mail_body)
        print(response)

    except Exception as e:
        print(f"Error sending email: {e}")

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
    flatpages.init_app(app)

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

app = create_app()