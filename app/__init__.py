# coding=utf-8
import os
from urllib.parse import quote_plus
from flask import Flask, render_template
from flask_login import LoginManager

from app.route.user import user
from app.route.admin import admin
from app.api import api
from app.api.model import db, User

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', '1frMFuWRVPV1')

# 数据库配置，支持环境变量
db_host = os.environ.get('DB_HOST', '127.0.0.1')
db_user = os.environ.get('DB_USER', 'root')
db_password = os.environ.get('DB_PASSWORD', '123456')
db_name = os.environ.get('DB_NAME', 'hotel')

# 对密码进行URL编码
db_password_encoded = quote_plus(db_password)
app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql://{db_user}:{db_password_encoded}@{db_host}/{db_name}"
db.init_app(app)

login_manager = LoginManager()
login_manager.login_view = '.login'
login_manager.init_app(app)
admin.init_app(app)

app.register_blueprint(user, url_prefix='/user')
app.register_blueprint(api, url_prefix='/api')

@login_manager.user_loader
def load_user(id):
        return User.query.get(int(id))

@app.route('/')
def index():
    return render_template('index.html')
