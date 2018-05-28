from . import index_blue
from flask import render_template,current_app

@index_blue.route('/')
def index():
    """主页"""
    return render_template('news/index.html')

@index_blue.route('/favicon.ico',methods=['GET'])
def favicon():
    return current_app.send_static_file('news/favicon.ico')