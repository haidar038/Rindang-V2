from App import db, admin
from flask_login import UserMixin
from datetime import datetime
from flask_admin.contrib.sqla.view import ModelView
from flask_admin.base import BaseView, expose
# from flask_admin.contrib.sqla import ModelView
# from flask_admin.menu import MenuLink
# from flask_login import current_user

now = datetime.now()

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    nama_lengkap = db.Column(db.String, nullable=True, default='')
    email = db.Column(db.String, nullable=False)
    username = db.Column(db.String, nullable=False, default='')
    password = db.Column(db.String, nullable=False)
    kelamin = db.Column(db.String, nullable=True, default='')
    pekerjaan = db.Column(db.String, nullable=True, default='')
    bio = db.Column(db.String, nullable=True, default='') 
    kelurahan_id = db.Column(db.Integer, db.ForeignKey('kelurahan.id'), nullable=True)
    account_type = db.Column(db.String, nullable=False, default='user')

    def __repr__(self):
        return f"User('{self.nama_lengkap}','{self.email}','{self.username}')"
    
class Kelurahan(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    nama = db.Column(db.String, nullable=True)
    kebun = db.Column(db.Integer, nullable=True)
    luas_kebun = db.Column(db.Float, nullable=True)
    komoditas = db.Column(db.String, nullable=True)
    jml_panen = db.Column(db.Integer, nullable=True)
    pangan_data = db.relationship('DataPangan', backref='kelurahan', lazy=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    kelurahan_id = db.Column(db.Integer, db.ForeignKey('kelurahan.id'), nullable=True)
    
class AppAdmin(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False)
    password = db.Column(db.String, nullable=False)
    account_type = db.Column(db.String(80), nullable=False, default='admin')

    def __repr__(self):
        return f"AppAdmin('{self.username}')"

class DataPangan(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    kebun = db.Column(db.String, nullable=False)
    komoditas = db.Column(db.String, nullable=False)
    jml_bibit = db.Column(db.Integer, nullable=False)
    tanggal_bibit = db.Column(db.String, nullable=False)
    jml_panen = db.Column(db.Integer, nullable=True, default=0)
    tanggal_panen = db.Column(db.String, nullable=True, default=0)
    status = db.Column(db.String, nullable=True, default='Penanaman')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    kelurahan_id = db.Column(db.Integer, db.ForeignKey('kelurahan.id'), nullable=True)

    def get_status_text(self):
        return "Active" if self.status else "Inactive"
