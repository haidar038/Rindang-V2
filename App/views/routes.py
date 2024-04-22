from flask import Blueprint, request, render_template, flash, redirect, url_for, jsonify, session
from flask_login import login_required, current_user
from flask_admin.base import expose, AdminIndexView, Admin
from werkzeug.security import check_password_hash, generate_password_hash
from sqlalchemy import asc
from datetime import datetime, timedelta
from babel.numbers import format_currency
import json, requests, ast

from App.models import User, DataPangan, Kelurahan
from App import db

views = Blueprint('views', __name__)

@views.route('/', methods=['POST', 'GET'])
def index():
    kelurahan = Kelurahan.query.all()
    produksi = DataPangan.query.all()

    if current_user.is_authenticated:
        if current_user.account_type == 'admin':
            return redirect(url_for('admin_page.index'))
        elif current_user.account_type == 'user':
            return redirect(url_for('views.dashboard'))

    today = datetime.today()
    kab_kota = 458 #Ternate
    komoditas_id = 3
    one_week_ago = today - timedelta(days=7)

    # Format dates as YYYY-MM-DD
    start_date = one_week_ago.strftime("%Y-%m-%d")
    end_date = today.strftime("%Y-%m-%d")

    url = f"https://panelharga.badanpangan.go.id/data/kabkota-range-by-levelharga/{kab_kota}/{komoditas_id}/{start_date}/{end_date}"

    response = requests.get(url)
    response.raise_for_status()

    data = response.json()

    target = ["Cabai Merah Keriting"]

    data_harga = []
    nama_komoditas = []

    for item in data["data"]:
        if item["name"] in target:
            komoditas = item["by_date"]
            data_harga.append(komoditas)
            nama_komoditas.append(item['name'])

    table_data = []

    for item in data["data"]:
        for date_data in item["by_date"]:
            date_obj = datetime.strptime(date_data["date"], "%Y-%m-%d")
            formatted_date = date_obj.strftime("%d/%m/%Y")

            # Handle cases where geomean is '-'
            geomean_value = date_data["geomean"]
            if geomean_value == "-":
                formatted_price = "-"
            else:
                geomean_float = float(geomean_value)

                # Remove decimal places
                # geomean_no_decimals = int(geomean_float)

                formatted_price = format_currency(geomean_float, "IDR", locale="id_ID", decimal_quantization=False)
                formatted_price = formatted_price[:-3]

            table_data.append({
                "date": formatted_date,
                "name": item["name"],
                "price": formatted_price
            })
    
    data_tanggal = []

    total_kebun = sum(kel.kebun for kel in kelurahan)
    total_panen = sum(prod.jml_panen for prod in produksi)

    for date_str in data['meta']['date']:
        data_tanggal.append(date_str)

    return render_template('index.html', table_data=table_data, kebun=total_kebun, produksi=total_panen, round=round)

# @views.route('/beranda', methods=['GET', 'POST'])
# #@login_required
# def home():
#     if current_user.is_authenticated and session['account_type'] == 'user':
#         postingan = DataPangan.query.all()
#         user = User.query.all()

#         if request.method == 'POST':
#             teks = request.form['tulisan']
#             anonym = True if request.form.get('anonim') == 'on' else False

#             cerita = DataPangan(konten=teks, tanggal=datetime.utcnow(), status=False, anonym=anonym, user_id=current_user.id)
#             db.session.add(cerita)
#             db.session.commit()
#             print('DataPangan berhasil dibuat!')
#             flash('Berhasil posting cerita!', 'success')
#             return redirect(request.referrer)
#         return render_template('beranda.html', postingan=postingan, user=user)
#     elif current_user.is_authenticated and session['account_type'] == 'admin':
#         return redirect(url_for('views.dashboard'))
#     else:
#         return redirect(url_for('auth.login'))
    
# @views.route('/profil/<string:username>', methods=['GET', 'POST'])
# #@login_required
# def profil(username):
#     if current_user.is_authenticated and session['account_type'] == 'user':
#         # user = User.query.filter_by(username=username)
#         user = User.query.filter_by(username=username).first()

#         if request.method == 'POST':
#             if user:
#                 password = request.form['password']
#                 if check_password_hash(user.password, password):
#                     user.nama_lengkap = request.form['nama_lengkap']
#                     user.username = request.form['username']
#                     user.email = request.form['email']
#                     user.password = generate_password_hash(request.form['password'], method='pbkdf2')
#                     db.session.commit()
#                     flash('Akun berhasil diubah!', category='success')
#                     print('Akun berhasil diperbarui!')
#                     return redirect(url_for('views.profil', username=username))
#                 else:
#                     flash("Kata sandi salah, silakan coba lagi.", category='danger')
#                     return redirect(url_for('views.profil', username=user.username))

#         post = DataPangan.query.filter_by(user_id=current_user.id).all()
#         return render_template("profil.html", user=user, post=post)
#     elif current_user.is_authenticated and session['account_type'] == 'admin':
#         return render_template("admin_profile.html")
#     else:
#         return redirect(url_for('auth.login'))

# @views.route('/about')
# def about():
#     return render_template('about.html')


# +++++++++++++++++++++++++++++++++++++ CHAT ROOM SESSION ++++++++++++++++++++++++++++++++++++++++

# page = request.args.get('page', 1, type=int)
# per_page = 10  # Ubah sesuai kebutuhan
# messages = Chat.query.filter_by(room_id=room).order_by(Chat.timestamp.desc()).paginate(page, per_page, error_out=False)
# chatContent = messages.items

# @views.route('/chat/<string:room>/', defaults={'page_num': 1})
# @views.route('/chat/<string:room>/<int:page_num>')
# #@login_required
# def chat(room, page_num):
#     user = User.query.all()
#     superuser = Admin.query.filter_by(account_type='admin').first()
#     if user or superuser:
#         msgs = Chat.query.filter_by(room_id=room).order_by(Chat.tanggal.desc()).paginate(page=page_num, per_page=5)
#         return render_template('chat_room.html', room=room, user=user, msgs=msgs, error_out=True)
#     else:
#         return "User not found", 404

# @views.route('/get_messages', methods=['GET'])
# def get_messages():
#     page = request.args.get('page', 1, type=int)
#     per_page = 10  # Ubah sesuai kebutuhan

#     messages = Chat.query.order_by(Chat.timestamp.desc()).paginate(page, per_page, error_out=False)
#     messages_data = [{'content': msg.content, 'user_id': msg.user_id} for msg in messages.items]

#     return jsonify({'messages': messages_data, 'has_next': messages.has_next})

# @views.route('/chat/delete_chat/<string:room>', methods=['GET'])
# def delete_chat(room):
#     # Use the SQLAlchemy delete() method to delete all rows
#     chat = Chat.query.filter_by(room_id=room).all()
#     for chats in chat:
#         db.session.delete(chats)
    
#     # Commit the changes to the database
#     db.session.commit()

#     return redirect(request.referrer)

# @socketio.on("connect")
# def connect():
#     print("Client connected!")

# @socketio.on('online')
# def online(data):
#     emit('status_change', {'username': data['username'], 'status': 'online'}, broadcast=True)

# @socketio.on("user_join")
# def user_join(room):
#     username = current_user.username
#     join_room(room)
#     if session['account_type'] == 'admin':
#         chats = Chat.query.filter_by(room_id=room).all()
#         for chat in chats:
#             chat.read = True
#         db.session.commit()
#     emit('join', {'username':username}, to=room)
#     print(f"Client {username} joined to {room}!")

# @socketio.on("new_message")
# def handle_message(message, room):
#     username = current_user.username
#     if room in rooms():
#         emit('chat', {'username':username, 'message':message}, broadcast=True, to=room)

#     print(f"New message: {message} from {username}")
#     msg_content = Chat(pesan=message, tanggal=datetime.utcnow(), sender=current_user.username, room_id=room, user_id=current_user.id)
#     db.session.add(msg_content)
#     db.session.commit()

# @socketio.on('leave')
# def leave(room):
#     username = current_user.username
#     room = room
#     print(f"{username} leave room")
#     leave_room(room)
#     emit('leave', {'username': username}, to=room)

# +++++++++++++++++++++++++++++++ CHAT ROOM SESSION ++++++++++++++++++++++++++=


# todo =========================== ADMIN SECTION =================================
# @views.route('/adminProfile/<string:username>', methods=['GET', 'POST'])
# #@login_required
# def adminProfile(username):
#     if current_user.is_authenticated and current_user.account_type == 'admin':
#         user = Admin.query.filter_by(username=username).first()

#         if request.method == 'POST':
#             if user:
#                 db.session.delete(user)
#                 db.session.commit()
#                 username = request.form['username']
#                 password = request.form['password']

#                 if check_password_hash(user.password, password):
#                     update_user = Admin(username=username, password=generate_password_hash(password, method='pbkdf2'))
#                     db.session.add(update_user)
#                     db.session.commit()
#                     flash('Akun berhasil diubah!', category='success')
#                     print('Akun berhasil diperbarui!')
#                     return redirect(url_for('views.adminProfile', username=username))
#         return render_template("admin_profile.html")
    
#     elif current_user.is_authenticated and current_user.account_type == 'user':
#         return render_template("profil.html")
#     else:
#         return redirect(url_for('auth.adminlogin'))

@views.route('/dashboard', methods=['GET', 'POST'])
#@login_required
def dashboard():
    user_data = User.query.all()
    pangan = DataPangan.query.all()
    return render_template('dashboard/index.html', user_data=user_data, pangan=pangan)
    # if current_user.is_authenticated:
    # else:
    #     return redirect(url_for('auth.login'))
        # chat = Chat.query.filter_by(read=False).all()
        # chat_counts = {user.room_id: sum(1 for chats in chat if chats.room_id == user.room_id and chats.read == False) for user in user_data}
    # elif current_user.is_authenticated and current_user.account_type == 'user':
    #     return redirect(url_for('views.home'))

@views.route('/dashboard/penjualan')
#@login_required
def penjualan():
    return render_template('dashboard/penjualan.html')

@views.route('/dashboard/data-pangan', methods=['POST','GET'])
#@login_required
def dataproduksi():
    user_data = User.query.filter_by(id=current_user.id).first()
    pangan = DataPangan.query.filter_by(user_id=current_user.id).all()
    kel = Kelurahan.query.filter_by(id=current_user.kelurahan_id).first()

    total_panen = []

    for total in pangan:
        panenTotal = total.jml_panen
        total_panen.append(panenTotal)

    # Persentase Kenaikan Produksi Pangan
    # kenaikan = round(((total_panen[-2] - total_panen[-1])/total_panen[-1])*100) if not 0 in total_panen else 0

    cabai = DataPangan.query.filter_by(user_id=current_user.id, komoditas='Cabai').order_by(asc(DataPangan.tanggal_panen)).all()
    tomat = DataPangan.query.filter_by(user_id=current_user.id, komoditas='Tomat').order_by(asc(DataPangan.tanggal_panen)).all()
    stat_cabai = []
    stat_tomat = []
    tgl_panen_cabai = []
    tgl_panen_tomat = []

    for panenCabai in cabai:
        totalCabai = panenCabai.jml_panen
        tglPanenCabai = panenCabai.tanggal_panen
        stat_cabai.append(totalCabai)
        tgl_panen_cabai.append(tglPanenCabai)
    for panenTomat in tomat:
        totalTomat = panenTomat.jml_panen
        tglPanenTomat = panenTomat.tanggal_panen
        stat_tomat.append(totalTomat)
        tgl_panen_tomat.append(tglPanenTomat)

    def calc_increase_cabai(stat_cabai):
    # Check if the list is empty or contains only one element
        if len(stat_cabai) < 2:
            return 0
        # Check if the list contains zero
        elif 0 in stat_cabai:
            return 0
        else:
            return round(((stat_cabai[-1] - stat_cabai[-2])/stat_cabai[-2])*100)
    
    def calc_increase_tomat(stat_tomat):
    # Check if the list is empty or contains only one element
        if len(stat_tomat) < 2:
            return 0
        # Check if the list contains zero
        elif 0 in stat_tomat:
            return 0
        else:
            return round(((stat_tomat[-1] - stat_tomat[-2])/stat_tomat[-2])*100)

    total_of_panen = sum(total_panen)
    totalPanenCabai = sum(stat_cabai)
    totalPanenTomat = sum(stat_tomat)

    print(stat_cabai)
    print(tgl_panen_cabai)

    if request.method == 'POST':
        kebun = request.form['kebun']
        komoditas = request.form['komoditas']
        jumlahBibit = request.form['jumlahBibit']
        tglBibit = request.form['tglBibit']
        # status = request.form['status']
        # jumlahPanen = request.form['jumlahPanen']
        # tglPanen = request.form['tglPanen']

        add_data = DataPangan(kebun=kebun, komoditas=komoditas, tanggal_bibit=tglBibit, jml_bibit=jumlahBibit, status='Penanaman', jml_panen=0, tanggal_panen=0, user_id=current_user.id)
        db.session.add(add_data)
        db.session.commit()
        print('DataPangan berhasil dibuat!')
        flash('Berhasil menginput data!', 'success')
        return redirect(request.referrer)
    return render_template('dashboard/data-pangan.html', kelurahan=kel, user_data=user_data, kenaikan_cabai=calc_increase_cabai(stat_cabai), kenaikan_tomat=calc_increase_tomat(stat_tomat), stat_cabai=json.dumps(stat_cabai), stat_tomat=json.dumps(stat_tomat), cabai=cabai, tomat=tomat, pangan=pangan, total_panen=total_of_panen, totalPanenCabai=totalPanenCabai, totalPanenTomat=totalPanenTomat, tgl_panen_cabai=json.dumps(tgl_panen_cabai), tgl_panen_tomat=json.dumps(tgl_panen_tomat))

@views.route('/dashboard/data-pangan/update-data/<int:id>', methods=['POST', 'GET'])
#@login_required
def updatepangan(id):
    pangan = DataPangan.query.get_or_404(id)
    kel = Kelurahan.query.filter_by(id=current_user.kelurahan_id).first()

    updateProd = request.form['updateProduksi']

    if updateProd == 'updateProduksi':
        if request.method == 'POST':
            kebun = request.form['updateKebun']
            komoditas = request.form['updateKomoditas']
            jumlahBibit = request.form['updateJumlahBibit']
            tglBibit = request.form['updateTglBibit']

            if pangan.status == 'Penanaman':
                jumlahPanen = DataPangan.query.filter_by(id=id)
                tglPanen = DataPangan.query.filter_by(id=id)

            pangan.kebun = kebun
            pangan.komoditas = komoditas
            pangan.jml_bibit = jumlahBibit
            pangan.tanggal_bibit = tglBibit

            db.session.commit()
            return redirect(url_for('views.dataproduksi'))
    elif updateProd == 'dataPanen':
        if request.method == 'POST':
            jumlahPanen = request.form['updateJumlahPanen']
            tglPanen = request.form['updateTglPanen']

            # totalKomod = DataPangan.query.filter_by()

            # total_panen = []

            # for total in pangan:
            #     panenTotal = total.jml_panen
            #     total_panen.append(panenTotal)

            # total_of_panen = sum(total_panen)

            pangan.status = 'Panen'
            pangan.jml_panen = jumlahPanen
            pangan.tanggal_panen = tglPanen
            pangan.kelurahan_id = kel.id

            kel.jml_panen = jumlahPanen
            # kel.komoditas = total_of_panen

            db.session.commit()
            return redirect(request.referrer)
        
@views.route('/dashboard/harga-pangan', methods=['POST', 'GET'])
#@login_required
def hargapangan():
    today = datetime.today()
    kab_kota = 458 #Ternate
    komoditas_id = 3
    one_week_ago = today - timedelta(days=7)

    # Format dates as YYYY-MM-DD
    start_date = one_week_ago.strftime("%Y-%m-%d")
    end_date = today.strftime("%Y-%m-%d")

    url = f"https://panelharga.badanpangan.go.id/data/kabkota-range-by-levelharga/{kab_kota}/{komoditas_id}/{start_date}/{end_date}"

    response = requests.get(url)
    response.raise_for_status()

    data = response.json()

    target = ["Cabai Merah Keriting", "Cabai Rawit Merah", "Bawang Merah"]

    data_harga = []
    nama_komoditas = []
    for item in data["data"]:
        if item["name"] in target:
            komoditas = item["by_date"]
            data_harga.append(komoditas)
            nama_komoditas.append(item['name'])
    table_data = []
    for item in data["data"]:
        for date_data in item["by_date"]:
            date_obj = datetime.strptime(date_data["date"], "%Y-%m-%d")
            formatted_date = date_obj.strftime("%d/%m/%Y")

            # Handle cases where geomean is '-'
            geomean_value = date_data["geomean"]
            if geomean_value == "-":
                formatted_price = "-"
            else:
                geomean_float = float(geomean_value)

                # Remove decimal places
                # geomean_no_decimals = int(geomean_float)

                formatted_price = format_currency(geomean_float, "IDR", locale="id_ID", decimal_quantization=False)
                formatted_price = formatted_price[:-3]

            table_data.append({
                "date": formatted_date,
                "name": item["name"],
                "price": formatted_price
            })
    
    data_tanggal = []
    for date_str in data['meta']['date']:
        data_tanggal.append(date_str)

    return render_template('dashboard/harga-pangan.html', data=data, table_data=table_data, dates=data_tanggal)

@views.route('/dashboard/data-pangan/delete-data/<int:id>', methods=['GET'])
#@login_required
def delete_data_pangan(id):
    data = DataPangan.query.get_or_404(id)
    db.session.delete(data)
    db.session.commit()
    return redirect(url_for('views.dataproduksi'))

# @views.route('/dashboard/approve_post/<int:id>', methods=['GET'])
# def approve_post(id):
#     post = DataPangan.query.get_or_404(id)
#     post.status = True
#     db.session.commit()
#     return redirect(url_for('views.dashboard'))

# @views.route('/delete_post/<int:id>', methods=['GET'])
# def delete_post(id):
#     post = DataPangan.query.get_or_404(id)
#     db.session.delete(post)
#     db.session.commit()
#     return redirect(url_for('views.dashboard'))

# todo ============== PROFILE PAGE ==============
@views.route('/dashboard/profil', methods=['GET', 'POST'])
#@login_required
def profil():
    user = User.query.filter_by(id=current_user.id).first()
    kelurahan = Kelurahan.query.filter_by(id=user.kelurahan_id).first()
    return render_template('dashboard/profil.html', user=user, kelurahan=kelurahan)

@views.route('/dashboard/profil/<int:id>/update', methods=['GET', 'POST'])
#@login_required
def updateprofil(id):
    user = User.query.get_or_404(id)
    kelurahan = Kelurahan.query.filter_by(user_id=current_user.id).first()

    form_type = request.form['formType']

    if form_type == 'Data User':
        if request.method == 'POST':
            user.nama_lengkap = request.form['nama']
            user.username = request.form['username']
            user.pekerjaan = request.form['pekerjaan']
            user.kelamin = request.form['kelamin']
            user.bio = request.form['bio']
            if not kelurahan:
                add_kelurahan = Kelurahan(user_id=current_user.id)
                db.session.add(add_kelurahan)
                db.session.commit()
                flash('Profil Berhasil Diubah', 'success')
                return redirect(url_for('views.profil'))
            else:
                user.kelurahan_id = kelurahan.id
                db.session.commit()
                flash('Profil Berhasil diubah!', 'success')
                return redirect(url_for('views.profil'))
    elif form_type == 'Data Kelurahan':
        if request.method == 'POST':
            if not kelurahan:
                add_kelurahan = Kelurahan(nama=request.form['kelurahan'], user_id=current_user.id)
                db.session.add(add_kelurahan)
                db.session.commit()
                flash('Profil Berhasil Diubah', 'success')
                return redirect(url_for('views.profil'))
            else:
                kelurahan.nama = request.form['kelurahan']
                kelurahan.kebun = request.form['kebun']
                kelurahan.luas_kebun = request.form['luaskebun']
                user.kelurahan_id = kelurahan.id
                db.session.commit()
                flash('Profil Berhasil diubah!', 'success')
                return redirect(url_for('views.profil'))

@views.route('/dashboard/pengaturan', methods=['GET', 'POST'])
#@login_required
def settings():
    user = User.query.filter_by(id=current_user.id).first()
    return render_template('dashboard/settings.html', user=user)

@views.route('/dashboard/pengaturan/<int:id>/update-email', methods=['GET', 'POST'])
#@login_required
def updateemail(id):
    user = User.query.get_or_404(id)
    password = request.form['userPass']

    if request.method == 'POST':
        if check_password_hash(current_user.password, password):
            user.email = request.form['email']
            db.session.commit()
            flash('Email berhasil diubah!', category='success')  # Assuming you have a flash message system
            return redirect((request.referrer))  # For successful update
        else:
            # Handle incorrect password scenario (e.g., flash a message or redirect)
            flash('Kata sandi salah, silakan coba lagi!', category='error')  # Assuming you have a flash message system
            return redirect(url_for('views.settings'))  # Redirect back to the form
        
@views.route('/dashboard/pengaturan/<int:id>/reset-profil', methods=['POST', 'GET'])
def resetprofil(id):
    kelurahan = Kelurahan.query.filter_by(user_id=id).first()

    if kelurahan:
        db.session.delete(kelurahan)
        db.session.commit()

        flash('Profil anda berhasil direset!', 'warning')
        return redirect(url_for('views.profil'))
    else:
        flash('Tidak ada data kelurahan!', 'warning')
        return redirect(url_for('views.profil'))

@views.route('/dashboard/pengaturan/<int:id>/update-password', methods=['GET', 'POST'])
#@login_required
def updatepassword(id):
    user = User.query.get_or_404(id)
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
            return redirect(url_for('views.settings'))  # Redirect back to the form

# @views.route('/dashboard/pengaturan/update-password/<int:id>', methods=['GET', 'POST'])
# def updatepassword(id):
#     user = User.query.get_or_404(id)
#     if request.method == 'POST':
#         user.password = request.form['userPass']

@views.route('/dashboard/prakiraan-cuaca', methods=['GET', 'POST'])
#@login_required
def weather():
    return render_template('dashboard/weather.html')

# @views.route('/profil/<string:username>', methods=['GET', 'POST'])
# #@login_required
# def profil(username):
#     if current_user.is_authenticated and session['account_type'] == 'user':
#         # user = User.query.filter_by(username=username)
#         user = User.query.filter_by(username=username).first()

#         if request.method == 'POST':
#             if user:
#                 password = request.form['password']
#                 if check_password_hash(user.password, password):
#                     user.nama_lengkap = request.form['nama_lengkap']
#                     user.username = request.form['username']
#                     user.email = request.form['email']
#                     user.password = generate_password_hash(request.form['password'], method='pbkdf2')
#                     db.session.commit()
#                     flash('Akun berhasil diubah!', category='success')
#                     print('Akun berhasil diperbarui!')
#                     return redirect(url_for('views.profil', username=username))
#                 else:
#                     flash("Kata sandi salah, silakan coba lagi.", category='danger')
#                     return redirect(url_for('views.profil', username=user.username))

#         post = DataPangan.query.filter_by(user_id=current_user.id).all()
#         return render_template("profil.html", user=user, post=post)
#     elif current_user.is_authenticated and session['account_type'] == 'admin':
#         return render_template("admin_profile.html")
#     else:
#         return redirect(url_for('auth.login'))

# @views.route('/about')
# def about():
#     return render_template('about.html')

# ========================= KELURAHAN SECTION =========================
@views.route('/peta-sebaran')
def mapbase():
    return render_template('kelurahan/map.html')

@views.route('/kelurahan-kulaba')
def kelkulaba():
    return render_template('kelurahan/kulaba.html')

@views.route('/kelurahan-sasa')
def kelsasa():
    return render_template('kelurahan/sasa.html')

@views.route('/kelurahan-kalumpang')
def kelkalumpang():
    return render_template('kelurahan/kalumpang.html')

@views.route('/kelurahan-santiong')
def kelsantiong():
    return render_template('kelurahan/santiong.html')

@views.route('/kelurahan-foramadiahi')
def kelforamadiahi():
    return render_template('kelurahan/foramadiahi.html')

@views.route('/kelurahan-tubo')
def keltubo():
    return render_template('kelurahan/tubo.html')

@views.route('/kelurahan-fitu')
def kelfitu():
    return render_template('kelurahan/fitu.html')

class MyHomeView(AdminIndexView):
    @expose('/')
    def index(self):
        user = User.query.all()
        return self.render('admin/index.html', user=user)

admin = Admin(index_view=MyHomeView())