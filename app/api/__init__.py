# coding=utf-8
from flask import Blueprint, request, abort, redirect, url_for, flash, jsonify
from flask_login import login_user, login_required, logout_user, current_user
from app.api.model import User, Hotel, Service, Config, db
import csv
import re

api = Blueprint('api', __name__)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ['csv']

@api.route('/regist', methods=['POST'])
def registBusiness():
    id_card = request.form.get('id_card')
    nowUser = User.query.filter_by(id_card=id_card).first()
    ban = Config.query.filter_by(key='ban').first()
    if ban and ban.value:
        flash('注册失败！已禁止注册')
        return redirect(url_for('apple.regist'))
    if not nowUser:
        name = request.form.get('name')
        password = request.form.get('password')
        group_number = request.form.get('group_number')
        phone = request.form.get('phone')
        user = User(name=name, id_card=id_card, password=password, group_number=group_number, phone=phone)
        db.session.add(user)
        db.session.commit()
        login_user(user)
        return redirect(url_for('apple.index'))
    flash('注册失败！帐号已存在')
    return redirect(url_for('apple.regist'))

@api.route('/login', methods=['POST'])
def loginBusiness():
    id_card = request.form.get('id_card')
    password = request.form.get('password')
    nowUser = User.query.filter_by(id_card=id_card, password=password).first()
    if nowUser:
        login_user(nowUser)
        if current_user.role == 10:
            return redirect(url_for('admin.index'))
        return redirect(url_for('apple.index'))
    flash('登录失败，请检查身份证号和密码！')
    return redirect(url_for('apple.login'))

@api.route('/logout', methods=['GET'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('apple.login'))

@api.route('/check_in', methods=['POST'])
@login_required
def check_in():
    if current_user.hotel:
        abort(400)
    hotel = Hotel.query.filter_by(check=False, clean=True).first()
    if hotel:
        hotel.check = True
        current_user.hotel = hotel
        db.session.commit()
        return jsonify(error=False, hotel={'block': hotel.block, 'room': hotel.room})
    return jsonify(error=True)

@api.route('/check_out', methods=['POST'])
@login_required
def check_out():
    if not current_user.hotel:
        abort(400)
    current_user.hotel.check = False
    current_user.hotel = None
    db.session.commit()
    return jsonify(error=False)

@api.route('/service', methods=['POST'])
@login_required
def service():
    type_val = request.form.get('type')
    content = request.form.get('content')
    service = Service(content=content, type=type_val, hotel=current_user.hotel)
    if type_val == '1':
        current_user.hotel.clean = False
    db.session.add(service)
    db.session.commit()
    return jsonify(error=False)

@api.route('/changepw', methods=['POST'])
@login_required
def changepw():
    old_password = request.form.get('old_password')
    new_password = request.form.get('new_password')
    if current_user.password == old_password:
        current_user.password = new_password
        db.session.commit()
        flash('修改密码成功！', 'success')
    else:
        flash('修改密码失败！原始密码错误！！', 'error')
    return redirect(url_for('apple.changepw'))

@api.route('/enter', methods=['POST'])
@login_required
def enter():
    file = request.files['fileName']
    if file and allowed_file(file.filename):
        reader = csv.reader(file)
        for index, line in enumerate(reader):
            if index == 0:
                continue
            try:
                db.session.add(User(id_card=line[0], name=line[1], phone=int(line[2]), password=line[3], group_number=current_user.group_number))
                db.session.commit()
            except:
                flash('录入失败！部分用户已存在！', 'error')
                return redirect(url_for('apple.checkgroup'))
        flash('录入成功！', 'success')
        return redirect(url_for('apple.checkgroup'))
    flash('录入失败！请使用指定模板创建文件', 'error')
    return redirect(url_for('apple.checkgroup'))

@api.route("/clear_database")
def clear_database():
    db.drop_all()
    db.create_all()
    db.session.add(User(id_card='admin', password='admin', role=10))
    db.session.add(Config(key='ban', value=0))
    for block in ['A', 'B', 'C']:
        rooms = []
        if block == 'A':
            rooms = list(range(102, 117)) + list(range(201, 217)) + list(range(301, 325))
        elif block == 'B':
            rooms = list(range(101, 122)) + list(range(201, 222)) + list(range(301, 322))
        else:
            rooms = list(range(101, 122)) + list(range(201, 222)) + list(range(301, 322))
        for r in rooms:
            db.session.add(Hotel(block=block, room=r))
    db.session.commit()
    return jsonify(error=False)
