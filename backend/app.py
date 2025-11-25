from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from functools import wraps
import os

app = Flask(__name__)

# Configuration de la base de données
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///notes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'votre-clé-secrète-très-difficile-à-deviner') # À changer en production

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)

# Modèles de données (utilisateurs et notes)
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='user') # Roles: user, admin

class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

# RBAC Decorator
def role_required(role):
    def wrapper(fn):
        @wraps(fn)
        @jwt_required()
        def decorator(*args, **kwargs):
            current_user = get_jwt_identity()
            user = User.query.filter_by(username=current_user['username']).first()
            if user and user.role == role:
                return fn(*args, **kwargs)
            else:
                return jsonify({"msg": "Accès non autorisé pour ce rôle"}), 403
        return decorator
    return wrapper

# Routes pour l'authentification
@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.get_json()
    hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
    new_user = User(username=data['username'], password=hashed_password)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": "Utilisateur créé avec succès"}), 201

@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data['username']).first()
    if user and bcrypt.check_password_hash(user.password, data['password']):
        access_token = create_access_token(identity={'username': user.username, 'role': user.role})
        return jsonify(token=access_token)
    return jsonify({"msg": "Nom d'utilisateur ou mot de passe incorrect"}), 401

# Routes pour les notes (protégées)
@app.route('/api/notes', methods=['GET'])
@jwt_required()
def get_notes():
    current_user = get_jwt_identity()
    user = User.query.filter_by(username=current_user['username']).first()
    notes = Note.query.filter_by(user_id=user.id).all()
    return jsonify([{'id': note.id, 'title': note.title, 'content': note.content} for note in notes])

@app.route('/api/notes', methods=['POST'])
@jwt_required()
def add_note():
    data = request.get_json()
    current_user = get_jwt_identity()
    user = User.query.filter_by(username=current_user['username']).first()
    new_note = Note(title=data['title'], content=data['content'], user_id=user.id)
    db.session.add(new_note)
    db.session.commit()
    return jsonify({'id': new_note.id, 'title': new_note.title, 'content': new_note.content}), 201

@app.route('/api/admin/notes', methods=['GET'])
@role_required('admin')
def get_all_notes():
    notes = Note.query.all()
    return jsonify([{'id': note.id, 'title': note.title, 'content': note.content, 'user_id': note.user_id} for note in notes])


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    # Exécution sans HTTPS pour le développement local car openssl n'est pas disponible
    app.run(host='0.0.0.0', debug=True, port=5000)
