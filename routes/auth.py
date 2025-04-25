import base64
import datetime
import secrets
from functools import wraps

import firebase_admin
import jwt
from firebase_admin import credentials, auth
from flask import request, jsonify, Blueprint

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)

auth_bp = Blueprint('auth', __name__)

key = secrets.token_bytes(32)
secret = base64.urlsafe_b64encode(key).decode('utf-8')
SECRET_KEY = secret

def verify_firebase_token(id_token):
    try:
        decoded_token = auth.verify_id_token(id_token)
        return decoded_token
    except Exception as e:
        print(f"Token verification failed: {e}")
        return None

def generate_custom_jwt(uid):
    payload = {
        "uid": uid,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(days=90),
        "iat": datetime.datetime.utcnow()
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    id_token = data.get("firebase_token")

    if not id_token:
        return jsonify({"error": "Missing Firebase token"}), 400

    decoded = verify_firebase_token(id_token)
    if not decoded:
        return jsonify({"error": "Invalid Firebase token"}), 401

    uid = decoded["uid"]
    custom_jwt = generate_custom_jwt(uid)

    return jsonify({"jwt": custom_jwt})

def jwt_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({"error": "Authorization header missing"}), 401

        token = auth_header.split(" ")[1]
        try:
            decoded = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            request.user = decoded
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401

        return f(*args, **kwargs)
    return decorated_function
