from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from application import app, db, status_dict, api_version, log_info
from model.user import User
from bson import ObjectId
from flask import request, jsonify
from werkzeug.security import generate_password_hash
from pymongo.errors import DuplicateKeyError
from bcrypt import checkpw, hashpw, gensalt
from flask_jwt_extended import create_access_token, JWTManager

login_manager = LoginManager()
login_manager.init_app(app)

jwt = JWTManager(app)

def get_user_by_username(username):
    user_data = db.users.find_one({"username": username})
    if user_data:
        return User(username=user_data["username"], password=user_data["password"], id=str(user_data["_id"]))
    return None


@app.route(f"/test")
@login_required
def test():
    return {"asd": str(db.users.find_one({"_id": ObjectId("642f302de82db80238da927c")}["_id"]))}

@app.route(f'/api/v{api_version}/login', methods=['POST'])
def login():
    username = request.json['username']
    password = request.json['password']
    
    user = get_user_by_username(username)

    if user and checkpw(password.encode("utf-8"), user.password):
        user_obj = User(user.id, user.username, user.password)
        # login_user(user_obj)
        return jsonify(create_access_token(identity=user.username))
        return jsonify({"message": "User logged in successfully", "user_id": user.id}), status_dict["OK"] 
    else:
        return jsonify({"error": "Wrong password"}), status_dict["GENERIC_ERROR"]


@app.route(f'/api/v{api_version}/register', methods=['POST'])
def register():
    data = request.get_json()

    if 'username' not in data or 'password' not in data:
        return jsonify({"error": "Missing username or password"}), status_dict["GENERIC_ERROR"]

    hashed_password = hashpw(data['password'].encode("utf-8"), gensalt())

    user = {
        "username": data['username'],
        "password": hashed_password
    }

    try:
        db.users.insert_one(user)
        return jsonify({"message": "User registered successfully"}), status_dict["OK"]
    except DuplicateKeyError:
        return jsonify({"error": "Username already exists"}), status_dict["GENERIC_ERROR"]


# @app.route(f'/api/v{api_version}/logout')
# @login_required
# def logout():
#     logout_user()
#     return redirect(url_for('login'))
