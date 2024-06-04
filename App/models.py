from App import db, admin
from flask_login import UserMixin
from datetime import datetime
from flask_admin.contrib.sqla.view import ModelView
from flask_admin.base import BaseView, expose

now = datetime.now()

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    nama_lengkap = db.Column(db.String(255), nullable=True, default='') # Ubah db.String menjadi db.String(255)
    email = db.Column(db.String(255), nullable=False) # Ubah db.String menjadi db.String(255)
    username = db.Column(db.String(255), nullable=False, default='') # Ubah db.String menjadi db.String(255)
    password = db.Column(db.String(255), nullable=False) # Ubah db.String menjadi db.String(255)
    kelamin = db.Column(db.String(50), nullable=True, default='') # Ubah db.String menjadi db.String(50)
    pekerjaan = db.Column(db.String(100), nullable=True, default='') # Ubah db.String menjadi db.String(100)
    bio = db.Column(db.String(255), nullable=True, default='') # Ubah db.String menjadi db.String(255)
    kelurahan_id = db.Column(db.Integer, db.ForeignKey('kelurahan.id'), nullable=True)
    account_type = db.Column(db.String(20), nullable=False, default='user') # Ubah db.String menjadi db.String(20)
    profile_pic = db.Column(db.String(255), nullable=True)

    def __repr__(self):
        return f"User('{self.nama_lengkap}','{self.email}','{self.username}')"
    
class Kelurahan(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    nama = db.Column(db.String(255), nullable=True) # Ubah db.String menjadi db.String(255)
    kebun = db.Column(db.Integer, nullable=True)
    luas_kebun = db.Column(db.Float, nullable=True)
    pangan_data = db.relationship('DataPangan', backref='kelurahan', lazy=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    
class AppAdmin(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), nullable=False) # Ubah db.String menjadi db.String(255)
    password = db.Column(db.String(255), nullable=False) # Ubah db.String menjadi db.String(255)
    account_type = db.Column(db.String(20), nullable=False, default='admin') # Ubah db.String menjadi db.String(20)

    def __repr__(self):
        return f"AppAdmin('{self.username}')"

class DataPangan(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    kebun = db.Column(db.String(255), nullable=False) # Ubah db.String menjadi db.String(255)
    komoditas = db.Column(db.String(255), nullable=False) # Ubah db.String menjadi db.String(255)
    jml_bibit = db.Column(db.Integer, nullable=False)
    tanggal_bibit = db.Column(db.String(50), nullable=False) # Ubah db.String menjadi db.String(50)
    jml_panen = db.Column(db.Integer, nullable=True, default=0)
    tanggal_panen = db.Column(db.String(50), nullable=True, default=0) # Ubah db.String menjadi db.String(50)
    status = db.Column(db.String(50), nullable=True, default='Penanaman') # Ubah db.String menjadi db.String(50)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    kelurahan_id = db.Column(db.Integer, db.ForeignKey('kelurahan.id'), nullable=True)

    def get_status_text(self):
        return "Active" if self.status else "Inactive"