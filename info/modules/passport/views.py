# 注册和登陆
from . import passport_blue


@passport_blue.route('/image_code',methods=['GET'])
def image_code():
    """提供图片验证码"""

    pass