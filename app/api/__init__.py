# coding=utf-8
import sys
reload(sys)
sys.setdefaultencoding('utf8')

from flask import Blueprint, request, abort, redirect, url_for, flash, jsonify
from flask.ext.login import login_user, login_required,logout_user, current_user
from app.api.model import User, Hotel, Service, Config, db
import csv
import re

api = Blueprint(
        'api',
        __name__,
)

def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1] in ['csv']

@api.route('/regist2', methods=['POST'])
@login_required
def regist2():
    id_card = request.form.get('id_card')
    nowUser = User.query.filter_by(id_card=id_card).first()
    if not nowUser:
        name = request.form.get('name')
        id_card = request.form.get('id_card')
        password = request.form.get('password')
        phone = request.form.get('phone')
        user = User(name=name, id_card=id_card, password=password, group_number=current_user.group_number, phone=phone)
        db.session.add(user)
        db.session.commit()
        flash('录入成功！')
        return redirect(url_for('apple.checkgroup'))
    else :
        flash('录入失败！该身份证已注册！')
    return redirect(url_for('apple.checkgroup'))

@api.route('/regist', methods=['POST'])
def registBusiness():
    id_card = request.form.get('id_card')
    nowUser = User.query.filter_by(id_card=id_card).first()
    ban = Config.query.filter_by(key='ban').first()
    if ban.value:
        flash('注册失败！已禁止注册')
    elif not nowUser:
        name = request.form.get('name')
        id_card = request.form.get('id_card')
        password = request.form.get('password')
        group_number = request.form.get('group_number')
        phone = request.form.get('phone')
        user = User(name=name, id_card=id_card, password=password, group_number=group_number, phone=phone)
        db.session.add(user)
        db.session.commit()
        login_user(user)
        return redirect(url_for('apple.index'))
    else :
        flash('注册失败！帐号已存在')
    return redirect(url_for('apple.regist'))

@api.route('/login',methods=['POST'])
def loginBusiness():
    id_card = request.form.get('id_card')
    password = request.form.get('password')
    nowUser = User.query.filter_by(id_card=id_card, password=password).first()
    if nowUser:
        login_user(nowUser)
        print current_user.role
        if (current_user.role == 10):
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
    if current_user.hotel != None:
        abort(400)
    hotel = Hotel.query.order_by(Hotel.id.asc()).filter_by(check=False, clean=True).first()
    if hotel:
        hotel.check = True
        current_user.hotel = hotel
        db.session.commit()
        return jsonify(error=False, hotel={'block': hotel.block, 'room':hotel.room})
    else :
        return jsonify(error=True)

@api.route('/check_out', methods=['POST'])
@login_required
def check_out():
    if current_user.hotel == None:
        abort(400)
    current_user.hotel.check = False
    current_user.hotel = None
    db.session.commit()
    return jsonify(error=False)

@api.route('/service', methods=['POST'])
@login_required
def service():
    type=request.form.get('type')
    content=request.form.get('content')
    service = Service(content, type, current_user.hotel)
    if type == '1':
        current_user.hotel.clean=False
    db.session.add(service)
    db.session.commit()
    return jsonify(error=False)

@api.route('/finish_service_medical/<int:id>', methods=['GET'])
@login_required
def finish_service_medical(id):
    service = Service.query.filter_by(id=id).first()
    if service:
        service.finish=1
        db.session.commit()
    return redirect(url_for('apple.checkmedical'))

@api.route('/finish_service/<int:id>', methods=['GET'])
@login_required
def finish_service(id):
    service = Service.query.filter_by(id=id).first()
    if service:
        service.finish=1
        service.hotel.clean=True
        db.session.commit()
    return redirect(url_for('apple.checkclean'))

@api.route('/changepw', methods=['POST'])
@login_required
def changepw():
    old_password = request.form.get('old_password')
    new_password = request.form.get('new_password')
    if( current_user.password == old_password ):
        current_user.password = new_password
        db.session.commit()
        flash('修改密码成功！', 'success')
    else : flash('修改密码失败！原始密码错误！！', 'error')
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
            line = [ bytes.decode(a) for a in line ]
            db.session.add(User(id_card=line[0], name=line[1],phone=int(line[2]), password=line[3], group_number=current_user.group_number))
        try:
            db.session.commit()
        except Exception,e:
            msg = re.search(r'(\'.*?\')', e[0], re.M|re.I).group(1)
            flash('录入失败！身份证号:%s 用户已存在！' % (msg), 'error')
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
    db.session.add(Config( key='ban', value=0 ))
    for i in range(0,3):
        if i == 0:
            block = 'A'
            for k in range (102,117):
                db.session.add(Hotel(block=block, room=k))
            for k in range (201,217):
                db.session.add(Hotel(block=block, room=k))
            for k in range (301,325):
                db.session.add(Hotel(block=block, room=k))
        elif i == 1:
            block = 'B'
            for k in range (101,122):
                db.session.add(Hotel(block=block, room=k))
            for k in range (201,222):
                db.session.add(Hotel(block=block, room=k))
            for k in range (301,322):
                db.session.add(Hotel(block=block, room=k))
        else :
            block = 'C'
            for k in range (101,122):
                db.session.add(Hotel(block=block, room=k))
            for k in range (201,222):
                db.session.add(Hotel(block=block, room=k))
            for k in range (301,322):
                db.session.add(Hotel(block=block, room=k))
    db.session.commit()
    return jsonify(error=False)
