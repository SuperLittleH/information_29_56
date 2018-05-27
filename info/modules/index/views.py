from . import index_blue
from info import redis_store

@index_blue.route('/')
def index():
    """主页"""
    redis_store.set('name','zxc')
    return "index"