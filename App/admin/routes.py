from flask import Blueprint, request, render_template, flash, redirect, url_for, make_response
from flask_login import login_required, logout_user, login_user, current_user
from datetime import datetime
import pdfkit, math
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
        kebunTotal = int(total.kebun)  # Konversi ke integer
        kebun.append(kebunTotal)

    total_of_panen = round(sum(total_panen)/1000)
    total_kebun = sum(kebun)
    
    if not current_user.is_authenticated:
        redirect(url_for('views.adminLogin'))
    return render_template('admin-dashboard/index.html', user=user, kelurahan=kelurahan, produksi=produksi, total_panen=total_of_panen, total_kebun=total_kebun)

@admin_page.route("/admin-dashboard/<int:id>/laporan", methods=['POST', 'GET'])
def report(id):
    today = datetime.utcnow()
    kel = Kelurahan.query.get_or_404(id)
    kmd = DataPangan.query.filter_by(kelurahan_id=kel.id).all()

    if request.method == 'POST':
        # Get the HTML content of the div with id "report"
        report_html = request.form['report_html']

        path_to_wkhtmltopdf = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'  # Replace with your path
        pdfkit.from_string(report_html, False, configuration=pdfkit.configuration(wkhtmltopdf=path_to_wkhtmltopdf))

        # Generate PDF using pdfkit
        pdf = pdfkit.from_string(report_html, False)

        # Create a response with the PDF data
        response = make_response(pdf)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = 'attachment; filename="report.pdf"'

        return response

    return render_template('admin-dashboard/laporan.html', today=today, kel=kel, kmd=kmd, round_numb=round)