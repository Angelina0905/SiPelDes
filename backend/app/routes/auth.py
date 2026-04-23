from flask import Blueprint, request, jsonify
from app import db
from app.models.user import User
from werkzeug.security import generate_password_hash, check_password_hash

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.json
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'Username sudah dipakai'}), 400
    user = User(
        username=data['username'],
        password=generate_password_hash(data['password']),
        role=data.get('role', 'warga')
    )
    db.session.add(user)
    db.session.commit()
    return jsonify({'message': 'Registrasi berhasil'}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    user = User.query.filter_by(username=data['username']).first()
    if not user or not check_password_hash(user.password, data['password']):
        return jsonify({'error': 'Username atau password salah'}), 401
    return jsonify({'message': 'Login berhasil', 'role': user.role, 'username': user.username})