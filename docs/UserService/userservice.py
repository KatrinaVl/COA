from flask import Flask, jsonify
from flask import request
from flask import make_response
import jwt
import json
import hashlib
import psycopg2

from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from datetime import datetime
from model import db, Register, UserInfo, ListFriends

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://user:password@database:5432/user_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'jwt_secret_key'

db.init_app(app)
jwt = JWTManager(app)

with app.app_context():
    db.create_all()

@app.route("/register", methods=['POST'])
def register():
    d = request.get_json(force=True)

    if Register.query.filter_by(login=d['login']).first():
        return {'message': 'Login already exists'}, 400

    if Register.query.filter_by(mail=d['mail']).first():
        return {'message': 'Email already exists'}, 400

    user = Register(login=d['login'],
        password=d['password'],
        mail=d['mail'],
        created_at=datetime.utcnow()
    )

    db.session.add(user)
    db.session.commit()

    user_ch = UserInfo(user_id=user.id, role= 'user',mail=d['mail'], token='tok')

    db.session.add(user_ch)
    db.session.commit()

    d_ans = {"user_id": user.id, 'message' : 'OK'}
    return jsonify(d_ans), 201

@app.route("/login", methods=['POST'])
def login():
    d = request.get_json(force=True)
    
    user = Register.query.filter_by(login=d['login']).first()
    if not user:
        return {'message' : "Please register"}, 401

    if user.password != d['password'] :
        return {'message' : "Wrong password"}, 401

    user_info = UserInfo.query.filter_by(user_id=user.id).first()
    if not user_info :
        return { 'message': "No info about user" }, 404

    token = create_access_token(identity=str(user.id))
    user_info.token = token[:99]
    db.session.commit()

    d_ans = {"token": token[:99], 'message' : 'OK'}

    return jsonify(d_ans), 201


@app.route("/update", methods=['PUT'])
def update():
    d = request.get_json(force=True)
    id_ = request.args.get("id")
    token = request.cookies.get('token')

    user = UserInfo.query.filter_by(user_id=id_).first()

    if (not user) :
        return {'message' : "impossible to find user"}, 404

    if token != user.token:
        return {'message' : "You do not have accses"}, 403

    if 'login' in d or 'password' in d:
        return {'message' : 'Impossible change login or password'}, 400

    columns = ['user_id', 'name', 'surname', 'phone', 'birthday', 'role', 'mail', 'status', 'token']
    for col in columns:
        if col in d:
            setattr(user, col, d[col])

    user.updated_at = datetime.utcnow()
    db.session.commit()

    return {'message' : "OK"}, 200

@app.route("/get_info", methods=['GET'])
def get_info():
    id_ = request.args.get("id")
    token = request.cookies.get('token')

    user = UserInfo.query.filter_by(user_id=id_).first()

    if (not user) :
        return {'message' : "impossible to find user" }, 404

    if token != user.token:
        return { 'message' : "You do not have accses"} , 403

    d_ans = user.as_dict()
    
    return jsonify(d_ans), 200

@app.route("/add_friend", methods=['PUT'])
def add_friend():
    d = request.get_json(force=True)
    id_ = request.args.get("id")
    id_friend = request.args.get("id_friend")
    token = request.cookies.get('token')

    user = UserInfo.query.filter_by(user_id=id_).first()
    friend_info = UserInfo.query.filter_by(user_id=id_friend).first()

    if (not user) :
        return {'message' : "impossible to find user" }, 404

    if (not friend_info) :
        return {'message' : "impossible to find friend user"} , 404

    if token != user.token:
        return {'message' : "You do not have accses"} , 403

    friend = ListFriends.query.filter_by(friend=id_friend).first()
    if (friend):
        return {'message' : "Friend already added"} , 400

    friend = ListFriends(user_id=user.id, friend= id_friend, name=d['name'], surname=d['surname'])

    db.session.add(friend)
    db.session.commit()
    
    return {'message' : "OK"} , 200


if __name__ == "__main__":
    
    app.run(debug=True, host='0.0.0.0', port='8091')