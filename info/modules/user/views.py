# 个人中心
from . import user_blue
from flask import  render_template,g,redirect,url_for,request,jsonify,current_app,session
from info.utils.comment import user_login_data
from info import response_code,db,constants
from info.utils.file_storage import upload_file

@user_blue.route('/pic_info',methods=['GET','POST'])
@user_login_data
def pic_info():
    """设置头像"""

    # 1.获取登陆信息
    user = g.user
    if not user:
        return redirect(url_for('index.index'))

    # 2.实现get请求逻辑
    if request.method == "GET":
        # 构造渲染数据的上下文
        context = {
            'user':user
        }

        # 渲染界面
        return render_template('news/user_pic_info.html',context=context)

    # 3.post请求逻辑:上传图片
    if request.method == "POST":
        # 3.1获取参数
        avatar_file = request.files.get('avatar')

        # 3.2校验参数
        try:
            avatar_data = avatar_file.read()
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=response_code.RET.PARAMERR, errmsg="读取头像数据失败")

        # 3.3调用上传的方法,将图片上传至七牛
        try:
            key = upload_file(avatar_data)
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=response_code.RET.THIRDERR, errmsg="上传失败")

        # 3.4保存用户头像的key到数据库
        user.avatar_url = key
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(e)
            return jsonify(errno=response_code.RET.DBERR, errmsg="保存用户头像失败")

        data = {
            'avatar_url': constants.QINIU_DOMIN_PREFIX + key
        }

        # 3.5响应头像的上传的结果
        return jsonify(errno=response_code.RET.OK, errmsg="上传成功", data=data)


@user_blue.route('/base_info',methods=['GET','POST'])
@user_login_data
def base_info():
    """基本资料"""

    #1.获取登录用户信息
    user = g.user
    if not user:
        return redirect(url_for('index.index'))

    # 2.实现GET请求的逻辑
    if request.method == "GET":
        # 构造渲染数据的上下文
        context = {
            'user':user
        }
        # 渲染界面
        return render_template('news/user_base_info.html',context=context)

    # 3.POST请求逻辑
    if request.method == "POST":
        # 3.1获取参数
        nick_name = request.json.get('nick_name')
        signature = request.json.get('signature')
        gender = request.json.get('gender')

        # 3.2校验参数
        if not all([nick_name,signature,gender]):
            return jsonify(errno=response_code.RET.PARAMERR, errmsg="缺少参数")
        if gender not in ['MAN','WOMAN']:
            return jsonify(errno=response_code.RET.PARAMERR, errmsg="参数错误")

        # 3.3修改用户的基本资料
        user.signature = signature
        user.nick_name = nick_name
        user.gender = gender

        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(e)
            return jsonify(errno=response_code.RET.DBERR, errmsg="修改用户资料失败")

        # 4.注意:修改了昵称以后记得将状态保持中的昵称也修改
        session['nick_name'] = nick_name

        # 5.响应修改结果
        return jsonify(errno=response_code.RET.OK, errmsg="修改基本资料成功")

@user_blue.route('/info')
@user_login_data
def user_info():
    """个人中心入口"""
    # 提示:必须是登录用户才能进入

    # 获取登录用户信息
    user = g.user
    if not user:
        return redirect(url_for('index.index'))

    context = {
        'user':user
    }

    return render_template('news/user.html',context=context)