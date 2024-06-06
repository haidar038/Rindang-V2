from flask import Blueprint, request, render_template, flash, redirect, url_for, session, Response
from flask_login import login_required, logout_user, login_user, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from App.models import User, AppAdmin
from App import db, login_manager

auth = Blueprint('auth', __name__)

# Define a custom error handler for unauthorized access
@auth.errorhandler(401)
def unauthorized(error):
    return Response(response="Unauthorized", status=401)

# User Loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    account_type = session.get('account_type')
    if account_type == 'admin':
        return AppAdmin.query.get(int(user_id))
    elif account_type == 'user':
        return User.query.get(int(user_id))
    else:
        return None

# Admin Login Route
@auth.route('/adminLogin', methods=['GET', 'POST'])
def adminLogin():
    """Handles admin login."""
    if current_user.is_authenticated:
        if current_user.account_type == 'admin':
            return redirect(url_for('admin_page.index'))
        else:
            return redirect(url_for('views.dashboard'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['userPassword']

        admin_user = AppAdmin.query.filter_by(username=username).first()

        if admin_user and check_password_hash(admin_user.password, password):
            session['account_type'] = 'admin'
            login_user(admin_user, remember=True)
            flash("Anda berhasil masuk!", category="success")
            return redirect(url_for('admin_page.index'))
        elif admin_user is None:
            flash(f"Akun dengan username {username} tidak ditemukan. Mungkin anda telah menggantinya!", category='warning')
            return redirect(url_for('auth.adminLogin'))
        else:
            flash("Kata sandi salah, coba lagi.", category='warning')
            return redirect(url_for('auth.adminLogin'))

    return render_template('admin-dashboard/login.html')

# User Login Route
@auth.route('/login', methods=['GET', 'POST'])
def login():
    """Handles user login."""
    if current_user.is_authenticated:
        if current_user.account_type == 'admin':
            return redirect(url_for('admin_page.index'))
        else:
            return redirect(url_for('views.dashboard'))

    email = request.form.get('emailAddress', '')  # Ambil nilai email dari form jika ada

    if request.method == 'POST':
        email = request.form['emailAddress']
        password = request.form['userPassword']

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            session['account_type'] = 'user'
            login_user(user, remember=True)
            flash("Berhasil Masuk!", category='success')
            return redirect(url_for('views.dashboard'))
        elif user is None:
            flash("Akun anda belum terdaftar, silakan daftar terlebih dahulu", category='warning')
            return redirect(url_for('auth.login', email=email))  # Teruskan nilai email saat redirect
        else:
            flash("Kata sandi salah, silakan coba lagi.", category='error')
            return redirect(url_for('auth.login', email=email))  # Teruskan nilai email saat redirect

    return render_template('login.html', page='User', email=email)  # Teruskan nilai email ke template

# User Registration Route
@auth.route('/register', methods=['GET', 'POST'])
def register():
    """Handles user registration."""
    if current_user.is_authenticated:
        if current_user.account_type == 'admin':
            return redirect(url_for('admin_page.index'))
        else:
            return redirect(url_for('views.dashboard'))

    if request.method == 'POST':
        email = request.form['emailAddress']
        password = request.form['userPass']
        confirm_password = request.form['userPassConf']

        if len(password) < 8:
            flash('Kata sandi harus berisi 8 karakter atau lebih', category='error')
        elif confirm_password != password:
            flash('Kata sandi tidak cocok.', category='error')
        elif User.query.filter_by(email=email).first():
            flash('Email sudah digunakan, silakan buat yang lain.', category='error')
        else:
            add_user = User(email=email, password=generate_password_hash(password, method='pbkdf2'))
            db.session.add(add_user)
            db.session.commit()
            flash('Akun berhasil dibuat!', category='success')
            
            # Log the user out explicitly after registration
            logout_user()

            return redirect(url_for('auth.login'))

    return render_template('register.html', page='User')

# Logout Route
@auth.route('/logout')
@login_required
def logout():
    """Handles user logout."""
    account_type = session.get('account_type')
    flash('You have logged out!', 'warning')
    logout_user()
    session.clear()

    if account_type == 'admin':
        return redirect(url_for('auth.adminLogin'))
    else:
        return redirect(url_for('auth.login'))