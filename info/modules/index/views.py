from . import index_blue


@index_blue.route('/')
def index():
    """主页"""
    return "index"