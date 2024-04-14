from flask import Blueprint, request, render_template, flash, redirect, url_for, make_response
from flask_login import login_required, logout_user, login_user, current_user
from datetime import datetime
from collections import defaultdict

from App.models import User, AppAdmin, DataPangan, Kelurahan
from App import db, admin, login_manager, socketio

admin_page = Blueprint('admin_page', __name__)

@admin_page.route("/admin-dashboard", methods=['POST', 'GET'])
@login_required
def index():
    user = User.query.all()
    kelurahan = Kelurahan.query.all()
    produksi = DataPangan.query.all()

    # Mengakumulasi total panen berdasarkan kelurahan_id
    total_panen_per_kelurahan = defaultdict(int)
    for data in produksi:
        total_panen_per_kelurahan[data.kelurahan_id] += data.jml_panen

    total_kebun = sum(kel.kebun for kel in kelurahan)
    total_panen = sum(prod.jml_panen for prod in produksi)
    
    if not current_user.is_authenticated:
        redirect(url_for('views.adminLogin'))
    return render_template('admin-dashboard/index.html', user=user, kelurahan=kelurahan, produksi=produksi, total_panen_per_kelurahan=total_panen_per_kelurahan, total_kebun=total_kebun, total_panen=total_panen, round_num=round)


@admin_page.route("/admin-dashboard/<int:id>/laporan", methods=['POST', 'GET'])
def report(id):
    today = datetime.utcnow()
    kel = Kelurahan.query.get_or_404(id)
    kmd = DataPangan.query.filter_by(kelurahan_id=kel.id).all()

    return render_template('admin-dashboard/laporan.html', today=today, kel=kel, kmd=kmd, round_numb=round)