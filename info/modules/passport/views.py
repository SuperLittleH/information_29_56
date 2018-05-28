# 注册和登陆
from . import passport_blue
from flask import request,abort,current_app,make_response
from info.utils.captcha.captcha import captcha
from info import redis_store,constants

@passport_blue.route('/image_code',methods=['GET'])
def image_code():
    """提供图片验证码"""
    # 1.接受参数
    # 2.效验参数
    # 3.生成图片验证码
    # 4.保存图片验证码到redis
    # 5.修改image的ContentType = 'image/jpg'
    # 6.响应图片验证码

    # 1.接受参数
    imageCodeId = request.args.get('imageCodeId')
    # 2.效验参数
    if not imageCodeId:
        abort(403)
    # 3.生成图片验证码
    name,text,image = captcha.generate_captcha()
    # 4.保存图片验证码redis
    try:
        redis_store.set('imageCode'+imageCodeId,text,constants.IMAGE_CODE_REDIS_EXPIRES)
    except Exception as e:
        current_app.logger.error(e)
        abort(500)
    # 5.修改image
    response = make_response(image)
    response.headers['Content-Type'] = 'image/jpg'


    #6.响应图片验证码
    return response