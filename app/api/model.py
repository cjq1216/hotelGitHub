# coding=utf-8
import sys
reload(sys)
sys.setdefaultencoding('utf8')

from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import UserMixin

from flask import Flask
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql://%s:%s@%s/%s" % ('root', '123456', '127.0.0.1', 'hotel')
db = SQLAlchemy(app)
import datetime

#db = SQLAlchemy()

class User(db.Model, UserMixin):

    __tablenanme__= 'user'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(15))
    id_card = db.Column(db.String(20), unique=True)
    phone = db.Column(db.Integer)
    password = db.Column(db.String(32))
    group_number = db.Column(db.Integer)
    role = db.Column(db.Integer)
    hotel_id = db.Column(db.Integer, db.ForeignKey('hotel.id'))
    hotel = db.relationship('Hotel', backref=db.backref('user', lazy='dynamic'))

    def __str__(self):
        return '用户<id:%s, 姓名:%s>' % (self.id, self.name)

    def __init__(self, name = None, id_card = None, password = None, group_number = None, phone = None, role = 0):
        self.name = name
        self.id_card = id_card
        self.password = password
        self.group_number = group_number
        self.phone = phone
        self.role = role

class Hotel(db.Model):

    __tablenanme__= 'hotel'
    id = db.Column(db.Integer, primary_key=True)
    block = db.Column(db.String(20))
    room = db.Column(db.Integer)
    check = db.Column(db.Boolean)
    clean = db.Column(db.Boolean)

    def __str__(self):
        return '房间<%s-%s>' % (self.block, self.room)

    def __init__(self, block = None, room = None, check = False, clean = True ):
        self.block = block
        self.room = room
        self.check =check
        self.clean = clean

class Service(db.Model):

    __tablenanme__= 'service'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(120))
    type = db.Column(db.Integer)
    hotel_id = db.Column(db.Integer, db.ForeignKey('hotel.id'))
    hotel = db.relationship('Hotel', backref=db.backref('service', lazy='dynamic'))
    finish = db.Column(db.Integer)

    def __str__(self):
        return '服务<%s-%s:%s>' % (self.hotel.block, self.hotel.room, self.content)

    def __init__( self, content=None, type=0, hotel=None ):
        self.content = content
        self.type = type
        self.hotel = hotel
        self.finish = 0

class Notice(db.Model):

    __tablenanme__= 'notice'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(30))
    content = db.Column(db.String(320))
    time = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    type = db.Column(db.Integer)

    def __str__(self):
        return '公告<%s>' % (self.title)

    def __init__( self, title = None, content = None, type = None ):
        self.title =title
        self.content = content
        self.type = type

class Config(db.Model):

    __tablenanme__= 'config'
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(30))
    value = db.Column(db.Integer)

    def __str__(self):
        return '%s:%s' % (self.key, self.value)

    def __init__( self, key=None, value=None ):
        self.key = key
        self.value = value
