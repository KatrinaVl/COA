from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Register(db.Model):
    __tablename__ = 'register'
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    mail = db.Column(db.String(100), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Register {self.login}>'

class UserInfo(db.Model):
    __tablename__ = 'userinfo'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('register.id'))
    name = db.Column(db.String(50))
    surname = db.Column(db.String(50))
    phone = db.Column(db.String(20))
    birthday = db.Column(db.Date)
    role = db.Column(db.String(20))
    mail = db.Column(db.String(100), db.ForeignKey('register.mail'))
    status = db.Column(db.String(20))
    token = db.Column(db.String(150))
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


    def __repr__(self):
        return f'<UserInfo {self.id}>'

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class ListFriends(db.Model):
    __tablename__ = 'listfriends'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('register.id'))
    friend = db.Column(db.Integer, db.ForeignKey('register.id'))
    name = db.Column(db.String(50))
    surname = db.Column(db.String(50))


    def __repr__(self):
        return f'<ListFriends {self.id}>'



