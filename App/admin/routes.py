from flask import Blueprint, request, render_template, flash, redirect, url_for, jsonify, session
from flask_login import login_required, logout_user, login_user, current_user
from flask_admin.base import BaseView, expose, AdminIndexView, Admin
from flask_socketio import emit, join_room, leave_room, send, rooms
from werkzeug.security import check_password_hash, generate_password_hash
from sqlalchemy import asc
from datetime import datetime, timedelta
from babel.numbers import format_currency
from xml.etree import ElementTree as ET
import urllib.request
import json, requests

from App.models import User, AppAdmin, DataPangan
from App import db, admin, login_manager, socketio

admin_page = Blueprint('admin_page', __name__)

@admin_page.route("/admin-dashboard", methods=['POST', 'GET'])
def index():
    return render_template('admin-dashboard/index.html')

@admin_page.route("/admin-dashboard/data-produksi", methods=['POST', 'GET'])
def dataproduksi():
    return render_template('admin-dashboard/data-produksi.html')

@admin_page.route("/admin-dashboard/data-kelurahan", methods=['POST', 'GET'])
def datakelurahan():
    return render_template('admin-dashboard/data-kelurahan.html')

@admin_page.route("/admin-dashboard/laporan", methods=['POST', 'GET'])
def report():
    return render_template('admin-dashboard/laporan.html')