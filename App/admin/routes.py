from flask import Blueprint, request, render_template, flash, redirect, url_for, make_response
from flask_login import login_required, current_user
from sqlalchemy import asc
# from flask_jwt_extended.tokens import _encode_jwt, _decode_jwt
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
from collections import defaultdict
from bs4 import BeautifulSoup
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, PageBreak, Paragraph, Image, Spacer, Flowable, KeepTogether
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm, mm
from reportlab.lib import colors
from reportlab.lib.utils import ImageReader
from reportlab.lib.styles import ParagraphStyle, TA_LEFT, TA_RIGHT, TA_CENTER
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

import io, os, base64, locale

from App.models import User, AppAdmin, DataPangan, Kelurahan, db
# from App import admin, login_manager, socketio

admin_page = Blueprint('admin_page', __name__)

# locale.setlocale(locale.LC_ALL, 'id_ID')

@admin_page.route("/admin-dashboard", methods=['POST', 'GET'])
@login_required
def index():
    if current_user.account_type == 'user':
        return redirect(url_for('views.dashboard'))

    user = User.query.all()
    kelurahan = Kelurahan.query.all()
    produksi = DataPangan.query.all()

    # Mengakumulasi total panen berdasarkan kelurahan_id
    total_panen_per_kelurahan = defaultdict(int)
    for data in produksi:
        try:
            total_panen_per_kelurahan[data.kelurahan_id] += data.jml_panen
        except Exception as e:
            # Menangani error jika terjadi saat menambahkan data ke total_panen_per_kelurahan
            print(f"Error saat menambahkan data panen ke total_panen_per_kelurahan: {e}")

    try:
        total_kebun = sum(kel.kebun for kel in kelurahan)
    except Exception as e:
        # Menangani error jika terjadi saat menghitung total_kebun
        print(f"Error saat menghitung total kebun: {e}")
        total_kebun = 0

    try:
        total_panen = sum(prod.jml_panen for prod in produksi)
    except Exception as e:
        # Menangani error jika terjadi saat menghitung total_panen
        print(f"Error saat menghitung total panen: {e}")
        total_panen = 0

    if not current_user.is_authenticated:
        redirect(url_for('views.adminLogin'))
    return render_template('admin-dashboard/index.html', user=user, kelurahan=kelurahan, produksi=produksi, total_panen_per_kelurahan=total_panen_per_kelurahan, total_kebun=total_kebun, total_panen=total_panen, round_num=round, genhash=generate_password_hash, checkhash=check_password_hash)

@admin_page.route('/admin-dashboard/<string:username>/profil', methods=['POST', 'GET'])
@login_required
def profile(username):
    print(current_user.account_type)
    user = AppAdmin.query.filter_by(username=username).first()
    return render_template('admin-dashboard/profile.html', user=user)

@admin_page.route('/admin-dashboard/<int:id>/profil/update-username', methods=['GET', 'POST'])
@login_required
def updateusername(id):
    user = AppAdmin.query.get_or_404(id)
    password = request.form['userPass']

    if request.method == 'POST':
        if check_password_hash(current_user.password, password):
            user.username = request.form['username']
            db.session.commit()
            flash('Username berhasil diubah!', category='success')  # Assuming you have a flash message system
            return redirect((request.referrer))  # For successful update
        else:
            # Handle incorrect password scenario (e.g., flash a message or redirect)
            flash('Kata sandi salah, silakan coba lagi!', category='error')  # Assuming you have a flash message system
            return redirect(url_for('admin_page.profile', username=user.username))  # Redirect back to the form
        
@admin_page.route('/admin-dashboard/<int:id>/profil/update-password', methods=['GET', 'POST'])
@login_required
def updatepassword(id):
    user = AppAdmin.query.get_or_404(id)
    oldpass = request.form['old-pass']
    newpass = request.form['new-pass']
    confnewpass = request.form['new-pass-conf']

    if request.method == 'POST':
        if check_password_hash(current_user.password, oldpass):
            if confnewpass != newpass:
                flash('Konfirmasi kata sandi tidak cocok!', 'error')
            else:
                user.password = generate_password_hash(newpass, method='pbkdf2')
                db.session.commit()
                flash('Kata sandi berhasil diperbarui!', category='success')  # Assuming you have a flash message system
                return redirect((request.referrer))  # For successful update
        else:
            # Handle incorrect password scenario (e.g., flash a message or redirect)
            flash('Kata sandi salah, silakan coba lagi!', category='error')  # Assuming you have a flash message system
            return redirect(url_for('admin_page.profile', username=user.username))  # Redirect back to the form

def get_chart_data():
    kelurahan_data = {}
    kelurahan_list = Kelurahan.query.all()

    for kelurahan in kelurahan_list:
        panen_data = (
            db.session.query(DataPangan.jml_panen, DataPangan.tanggal_panen, DataPangan.komoditas)
            .filter_by(kelurahan_id=kelurahan.id)  # Hapus filter user_id
            .order_by(asc(DataPangan.tanggal_panen))
            .all()
        )

        if kelurahan.nama not in kelurahan_data:
            kelurahan_data[kelurahan.nama] = {}

        for data in panen_data:
            jml_panen, tgl_panen, komoditas = data
            if komoditas not in kelurahan_data[kelurahan.nama]:
                kelurahan_data[kelurahan.nama][komoditas] = {
                    'jml_panen': [],
                    'tgl_panen': [],
                    'komoditas': []
                }
            kelurahan_data[kelurahan.nama][komoditas]['jml_panen'].append(jml_panen)
            kelurahan_data[kelurahan.nama][komoditas]['tgl_panen'].append(tgl_panen)
            kelurahan_data[kelurahan.nama][komoditas]['komoditas'].append(komoditas)

    return kelurahan_data

@admin_page.route('/admin-dashboard/data-produksi', methods=['POST', 'GET'])
@login_required
def dataproduksi():
    if current_user.account_type == 'user':
        return redirect(url_for('views.dashboard'))

    chart_data = get_chart_data()

    print(chart_data)

    return render_template('admin-dashboard/data-produksi.html', chart_data=chart_data)

@admin_page.route('admin-dashboard/data-produksi/<int:id>', methods=['POST', 'GET'])
@login_required
def dataproduksikel(id):
    if current_user.account_type == 'user':
        return redirect(url_for('views.dashboard'))
    
    kelurahan = Kelurahan.query.get_or_404(id)
    kelurahan_data = {}

    panen_data = (
        db.session.query(DataPangan.jml_panen, DataPangan.tanggal_panen, DataPangan.komoditas)
        .filter_by(kelurahan_id=kelurahan.id)  # Hapus filter user_id
        .order_by(asc(DataPangan.tanggal_panen))
        .all()
    )

    if kelurahan.nama not in kelurahan_data:
        kelurahan_data[kelurahan.nama] = {}

    for data in panen_data:
        jml_panen, tgl_panen, komoditas = data
        if komoditas not in kelurahan_data[kelurahan.nama]:
            kelurahan_data[kelurahan.nama][komoditas] = {
                'jml_panen': [],
                'tgl_panen': [],
                'komoditas': []
            }
        kelurahan_data[kelurahan.nama][komoditas]['jml_panen'].append(jml_panen)
        kelurahan_data[kelurahan.nama][komoditas]['tgl_panen'].append(tgl_panen)
        kelurahan_data[kelurahan.nama][komoditas]['komoditas'].append(komoditas)

    return render_template('/admin-dashboard/data-kelurahan.html', chart_data=kelurahan_data, kelurahan=kelurahan)

@admin_page.route("/admin-dashboard/laporan/userid?=<int:id>/<string:nama>", methods=['POST', 'GET'])
# @login_required
def report(nama, id):
    from App.app import app
    # if current_user.account_type == 'user':
    #     return redirect(url_for('views.dashboard'))

    # Register Font    
    font_dir = os.path.join(app.root_path, 'static', 'fonts', 'plusjakarta')
    for font_file in os.listdir(font_dir):
        if font_file.endswith('.ttf'):
            font_path = os.path.join(font_dir, font_file)
            with open(font_path, 'rb') as f:  # Buka file font dalam mode biner
                font_name = font_file[:-4]
                pdfmetrics.registerFont(TTFont(font_name, f))
    kel = Kelurahan.query.get_or_404(id)

    nama = check_password_hash(nama, kel.nama)

    today = datetime.utcnow()
    kmd = DataPangan.query.filter_by(kelurahan_id=kel.id).all()

    # Render template HTML dengan data
    html = render_template('admin-dashboard/laporan.html', today=today, kel=kel, kmd=kmd, round_numb=round)

    # Buat buffer file
    buffer = io.BytesIO()

    # Parsing HTML dan ekstrak data tabel
    soup = BeautifulSoup(html, 'html.parser')
    table = soup.find('table')

    # print(table)
    
    # Periksa apakah tabel ditemukan
    if table is None:
        raise ValueError("Tabel dengan id 'report' tidak ditemukan dalam HTML")

    # Buat dokumen PDF
    BASE_MARGIN = 2 * cm
    page_width, page_height = A4
    total_margin_width = 2 * BASE_MARGIN
    available_table_width = page_width - total_margin_width
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        topMargin=BASE_MARGIN,  # Increased top margin
        leftMargin=BASE_MARGIN,
        rightMargin=BASE_MARGIN,
        bottomMargin=BASE_MARGIN
    )

    # Ekstrak data tabel
    data = []
    for row in table.find_all('tr'):
        cells = row.find_all('td')
        if not cells:  # Jika tidak ada sel data, gunakan sel header
            cells = row.find_all('th')
        data.append([cell.text.strip() for cell in cells])
    
    h1_style = ParagraphStyle(name='Heading1', fontName='PlusJakartaSans-Bold', fontSize=22, alignment=TA_CENTER)
    normal_style = ParagraphStyle(name='Normal', fontName='PlusJakartaSans-Regular', fontSize=12)
    date_style = ParagraphStyle(name='Date', fontName='PlusJakartaSans-Italic', fontSize=10, alignment=TA_RIGHT, textColor=colors.gray)
    
    col_widths = [available_table_width / len(data[0])] * len(data[0])
    table_width = page_width - 2 * BASE_MARGIN
    table_style = TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.Color(0.533, 0.788, 0.482)),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'PlusJakartaSans-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        # ('BOX', (0, 0), (-1, -1), 1, colors.gray),
        ('GRID', (0, 0), (-1, -1), 0.25, colors.Color(0,0,0,0.25)),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),  # Align text to the top
        # ('ALIGN', (1, 0), (-1, -1), 'CENTER'),  # Center align text in columns 1 and onwards
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),  # Center align text in columns 1 and onwards
        ('ALIGN', (0, 0), (0, -1), 'CENTER'),  # Center align text in columns 1 and onwards
    ])

    # for i in range(len(data)):
    #     table_style.add('LINEABOVE', (0,i), (-1,i), 1, colors.gray)
    #     table_style.add('LINEBELOW', (0,i), (-1,i), 1, colors.gray)

    # Buat tabel
    table = Table(data, style=table_style, rowHeights=1*cm, colWidths=[1.25*cm, 3.85*cm],
              repeatRows=1, splitByRow=True, hAlign='CENTER')
    title = Paragraph("Laporan Produksi", h1_style )

    # Buat elemen-elemen untuk dokumen
    # elements.append(table)

    # Logo
    logo_path = os.path.join(app.root_path, 'static', 'logo', 'rindang-logo-y.png')
    
    # Dapatkan ukuran gambar asli
    image_reader = ImageReader(logo_path)
    img_width, img_height = image_reader.getSize()
    aspect_ratio = img_width / img_height

    # Tentukan tinggi gambar yang diinginkan
    desired_height = 12*mm
    # Hitung lebar gambar berdasarkan rasio aspek
    desired_width = desired_height * aspect_ratio

    # Buat objek Image dengan ukuran yang dihitung
    today = Paragraph(today.strftime('%A, %d %B %Y'), date_style)

    logo = Image(logo_path, width=desired_width, height=desired_height, hAlign='LEFT')
    logo_and_time = Table([[logo, today]], colWidths=[desired_width, table_width - desired_width])
    logo_and_time.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),  # Vertically align logo and title in the middle
    ]))

    elements = [
        logo_and_time,
        Spacer(0, 15),
        title,
        Spacer(0, 32),
        Paragraph(f"Kelurahan: {kel.nama}", normal_style),
        Spacer(0, 4),
        Paragraph(f"Jumlah Kebun: {kel.kebun} Kebun", normal_style),
        Spacer(0, 15),
        table
    ]

    # doc.build([layout_table], canvasmaker=canvas.Canvas)
    doc.build(elements, canvasmaker=canvas.Canvas)

    # Reset posisi buffer ke awal
    buffer.seek(0)

    # Encode data PDF menjadi base64
    # pdf_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')

    response = make_response(buffer.getvalue())
    # response.headers['Content-Disposition'] = f'attachment; filename=Report_of_{kel.nama}.pdf'
    
    response.headers['Content-Disposition'] = f'inline; filename=Report_of_{kel.nama}.pdf'
    response.mimetype = 'application/pdf'

    response.set_cookie('pdf-filename', f'Report_of_{kel.nama}.pdf')
    response.direct_passthrough = True  # Prevent automatic download

    pdf_value = buffer.getvalue()
    buffer.close()

    return response
    return render_template('admin-dashboard/laporan.html', today=today, kel=kel, kmd=kmd, round_numb=round)