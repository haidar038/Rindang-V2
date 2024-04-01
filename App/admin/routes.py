from flask import Blueprint, request, render_template, flash, redirect, url_for, jsonify, session, send_file
from flask_login import login_required, logout_user, login_user, current_user
from datetime import datetime
import pdfkit
# from weasyprint import HTML

from App.models import User, AppAdmin, DataPangan, Kelurahan
from App import db, admin, login_manager, socketio

admin_page = Blueprint('admin_page', __name__)

@admin_page.route("/admin-dashboard", methods=['POST', 'GET'])
@login_required
def index():
    user = User.query.all()
    kelurahan = Kelurahan.query.all()
    produksi = DataPangan.query.all()

    total_panen = []
    kebun = []

    for total in produksi:
        panenTotal = total.jml_panen
        total_panen.append(panenTotal)

    for total in kelurahan:
        kebunTotal = total.kebun
        kebun.append(kebunTotal)

    total_of_panen = sum(total_panen)
    total_kebun = sum(kebun)
    
    if not current_user.is_authenticated:
        redirect(url_for('views.adminLogin'))
    return render_template('admin-dashboard/index.html', user=user, kelurahan=kelurahan, produksi=produksi, total_panen=total_of_panen, total_kebun=total_kebun)

@admin_page.route("/admin-dashboard/laporan", methods=['POST', 'GET'])
def report():
    today = datetime.utcnow()

    if request.method == ['POST']:
        html_string = request.form.get('.report')
        pdf = pdfkit.from_string(html_string, False)

        return send_file(pdf, mimetype='application/pdf', download_name='laporan.pdf')
    return render_template('admin-dashboard/laporan.html', today=today)