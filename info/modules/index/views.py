from . import index_blue
from flask import render_template

@index_blue.route('/')
def index():
    """主页"""

    return render_template('news/index.html')