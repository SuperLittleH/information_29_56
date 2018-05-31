# 新闻详情
from flask import  render_template
from . import news_blue


@news_blue.route('/detail/<int:news_id>')
def news_detail(news_id):
    """新闻详情
    """
    # 渲染模板
    return render_template('news/detail.html')