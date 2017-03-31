# coding=utf-8
from flask import render_template, Blueprint, redirect, url_for, request, session, current_app
from flask.ext.login import login_required, current_user
from app.api.model import User, Service, Hotel, Notice
import random

user = Blueprint(
        'apple',
        __name__
)

@user.route('/')
def index():
    return render_template('index.html')

@user.route('/checkin')
@login_required
def checkin():
    return render_template('checkin.html')

@user.route('/service')
@login_required
def service():
    return render_template('service.html')

@user.route('/checkclean')
@login_required
def checkclean():
    block = current_user.id_card[0]
    room = int(current_user.id_card[1])
    hotels = Hotel.query.with_entities(Hotel.room, Hotel.block, Service.id, Service.finish, Service.content, User.name\
        ).order_by( Service.id.desc()).join(Service, Service.hotel_id == Hotel.id ).join(\
        User, User.hotel_id == Hotel.id ).filter(\
        Hotel.room > room*100, Hotel.room < (room+1)*100, Hotel.block==block, Service.type==1).all()
    return render_template('checkclean.html', hotels=hotels)

@user.route('/checkgroup')
@login_required
def checkgroup():
    users = User.query.filter_by(group_number=current_user.group_number);
    return render_template('checkgroup.html', users=users)

@user.route('/checkmedical')
@login_required
def checkmedical():
    block = current_user.id_card[0]
    print block
    hotels = Hotel.query.with_entities(Hotel.room, Hotel.block, Service.id, Service.finish, Service.content, User.name\
        ).order_by( Service.id.desc()).join(Service, Service.hotel_id == Hotel.id ).join(\
        User, User.hotel_id == Hotel.id ).filter(\
        Hotel.block==block, Service.type==2).all()
    return render_template('checkmedical.html', hotels=hotels)

@user.route('/login')
def login():
    return render_template('signin.html')

@user.route('/regist')
def regist():
    return render_template('register.html')

@user.route('/changepw')
@login_required
def changepw():
    return render_template('changepw.html')

@user.route('/notice')
@login_required
def notice():
    if current_user.role == 0 :
        type = 0
    else :
        type = 1
    notices = Notice.query.filter_by(type = type)
    return render_template('notice.html', notices=notices)
