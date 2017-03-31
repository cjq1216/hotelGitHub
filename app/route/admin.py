# coding=utf-8
import sys
reload(sys)
sys.setdefaultencoding('utf8')

from flask.ext.admin import Admin, expose
from flask_admin.contrib.sqla import ModelView
from flask_admin import AdminIndexView
from app.api.model import User, Hotel, Service, Notice, Config, db
from flask import redirect, url_for, render_template, request, jsonify
from flask.ext.login import current_user, logout_user


class MyView(AdminIndexView):
    @expose('/')
    def index(self):
        if current_user.is_authenticated and current_user.role == 10:
            return super(MyView, self).index()
        else :
            return redirect(url_for('apple.login'))

    @expose('/checkUser')
    def checkUser(self):
        if current_user.is_authenticated and current_user.role == 10:
            id = request.args.get('id')
            user = User.query.filter_by(id=id).first()
            if user == None or user.authentication == True:
                return jsonify({'flag':False})
            user.authentication = True
            db.session.commit()
            return jsonify({'flag':True})
        else :
            return jsonify({'flag':False})


class MyModelView(ModelView):
    column_display_pk=True
    column_default_sort = ('id', True)
    can_create = True
    column_searchable_list = ['id']
    def is_accessible(self):
        return current_user.is_authenticated and current_user.role == 10

    def inaccessible_callback(self, name, **kwargs):
        # redirect to login page if user doesn't have access
        return redirect(url_for('.login'))


admin = Admin(name="后台管理系统", index_view=MyView(), base_template='admin-master.html')
admin.add_view(MyModelView(User, db.session, name='用户'))
admin.add_view(MyModelView(Hotel, db.session, name='房间'))
admin.add_view(MyModelView(Service, db.session, name='服务'))
admin.add_view(MyModelView(Notice, db.session, name='公告'))
admin.add_view(MyModelView(Config, db.session, name='配置'))
