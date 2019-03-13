import datetime
from functools import cmp_to_key

import pymysql
from flask import make_response
from flask import render_template, jsonify
from flask import request

import config
from flask import Flask

import database
import task
import utils

app = Flask(__name__)


@app.route('/')
def hello_world():
    return render_template('index.html')

@app.route('/test_db')
def test_db():
    state = 'stoped'
    db = pymysql.connect(config.database_config['host'], config.database_config['user'], config.database_config['passwd'], config.database_config['db_name'])
    cursor = db.cursor()
    try:
        results = cursor.execute('show tables')
        print(results)
        state = 'running'
    except Exception as e:
        print(e)
        state = 'stoped'
    db.close()
    return state

@app.route('/observable_list')
@app.route('/observable_list/user/<int:subscriber_id>')
@app.route('/observable_list/label/<int:label_id>')
@app.route('/observable_list/label/<int:label_id>/user/<int:subscriber_id>')
def observable_list(subscriber_id = None,label_id = None):
    '''
    商品监控列表
    :return:
    '''
    subscriber = None
    if not subscriber_id:
        subscriber_id = request.cookies.get('user_id')
    subscriber = database.getSubscriber(subscriber_id)

    label = database.getLabel(label_id) # 用于从归类页点击到商品页时加一行标签信息

    observables = database.getObservableAll(label_id)
    for obs in observables :
        if subscriber_id:
            obs.v_subscribe = database.getSubscribe(subscriber_id, obs.id)

        if obs.label_id:
            obs.v_label = database.getLabel(obs.label_id) # 用于取历史最低价

        items = database.getItems(obs.url,-20)
        if items and len(items):
            # print(items[0])
            obs.v_item = items[0]
            for item in items:
                if item.min_price != items[0].min_price:
                    obs.v_trend = items[0].min_price - item.min_price
                    break
    if observables:
        # 排序 把没有订阅的放到后这
        observables.sort(key=cmp_to_key(utils.obs_cmp))

    #标签
    labels = database.getLabelAll()

    return render_template('observable_list.html',list = observables,label = label,user = subscriber,labels = labels)

@app.route('/item_list/<int:id>/<int:total>')
def item_list(id,total):
    '''
    最新抓取结果
    :param id:
    :return:
    '''
    data = []
    if id:
        observable = database.getObservable(id)
        if observable:
            items = database.getItems(observable.url, total*-1)
            for item in items:
                data.append(item.jsonStr())
    return jsonify(data);

@app.route('/add_subscribe',methods=['POST'])
def add_subscribe():
    '''
    订阅商品
    :return:
    '''
    if request.method == 'POST':
        mail = request.form['mail']
        url = request.form['url']
        hope_price = request.form['hope_price']
        label_id = request.form['label_id']
        url = utils.trimUrl(url)
        if mail and url and label_id:
            subscriber = database.addSubscriber(mail)
            if subscriber:
                task.subscribe(subscriber.id,url,label_id,hope_price)
                observable = database.getObservableByUrl(url)
                if observable:
                    observables = []
                    observables.append(observable)
                    task.classifyCaptureSave(observables)
            return "success"
        else:
            return "邮箱或商品链接或标签无效"

@app.route('/unsubscribe/<int:observable_id>/<int:subscriber_id>')
def unsubscribe(observable_id,subscriber_id):
    '''
    取消订阅
    :param subscriber_id:
    :param observable_id:
    :return:
    '''
    return jsonify(database.delSubscribeById(subscriber_id,observable_id))

@app.route('/add_label',methods=['POST','GET'])
def add_label():
    '''
    创建标签
    :return:
    '''
    if request.method == 'POST':
        name = request.form['label_name']
        lowest_price = request.form['lowest_price']
        if name:
            if not lowest_price :
                lowest_price = 0
            database.addLabel(name,lowest_price)
            return "success"
        else:
            return "标签名无效"

@app.route('/label_list')
def label_list():
    '''
    标签列表
    :return:
    '''
    labels = database.getLabelAll()

    for lab in labels:
        observables = database.getObservableAll(lab.id)
        for obs in observables:
            items = database.getItems(obs.url,-20)
            if items and len(items):

                # 当前最低价
                if lab.v_min_pirce == 0:
                    lab.v_min_pirce = items[0].min_price
                    lab.date = items[0].date  # 更新日期
                elif lab.v_min_pirce > items[0].min_price:
                    lab.v_min_pirce = items[0].min_price
                    lab.date = items[0].date  # 更新日期



    return render_template('label_list.html',labels = labels)

@app.route('/login_or_regist',methods=['POST'])
def login_or_regist():
    '''
    登录或注册
    :return:
    '''
    if request.method == 'POST':
        mail = request.form['mail']
        if mail:
            subscriber = database.addSubscriber(mail)
            if subscriber:
                resp = make_response("success")
                outdate = datetime.datetime.today() + datetime.timedelta(days=7) # 有效期7天
                resp.set_cookie("user_id",str(subscriber.id),expires = outdate)
                return resp
            else:
                return "注册失败"
        else:
            return "邮箱无效"


if __name__ == '__main__':
    app.run(debug=True)
