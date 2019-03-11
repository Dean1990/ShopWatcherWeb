import json
from functools import cmp_to_key

import pymysql
import time
from flask import redirect
from flask import render_template, jsonify
from flask import request
from flask import url_for

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
@app.route('/observable_list/<int:subscriber_id>')
def observable_list(subscriber_id = None):
    '''
    商品监控列表
    :return:
    '''
    subscriber = None
    if subscriber_id:
        subscriber = database.getSubscriber(subscriber_id)

    observables = database.getObservableAll()
    for obs in observables :
        if subscriber_id:
            subscribe = database.getSubscribe(subscriber_id, obs.id)
            obs.v_subscribe = subscribe

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
    return render_template('observable_list.html',list = observables,user = subscriber)

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

@app.route('/add_subscribe',methods=['POST','GET'])
@app.route('/add_subscribe/<int:observable_id>/<int:subscriber_id>',methods=['POST','GET'])
def add_subscribe(observable_id = None,subscriber_id = None):
    '''
    订阅商品
    :return:
    '''
    if request.method == 'POST':
        mail = request.form['mail']
        url = request.form['url']
        hope_price = request.form['hope_price']
        url = utils.trimUrl(url)
        if mail and url:
            subscriber = database.addSubscriber(mail)
            if subscriber:
                if not hope_price:
                    hope_price = 0
                task.subscribe(subscriber.id,url,hope_price)
                observable = database.getObservableByUrl(url)
                if observable:
                    observables = []
                    observables.append(observable)
                    task.classifyCaptureSave(observables)
        else:
            return "邮箱和商品链接不能为空"
        return redirect(url_for('observable_list',subscriber_id = subscriber.id))
    else:
        url = ''
        mail = ''
        if observable_id:
            observable = database.getObservable(observable_id)
            if observable :
                url = observable.url
        if subscriber_id:
            subscriber = database.getSubscriber(subscriber_id)
            if subscriber:
                mail = subscriber.mail
        return render_template('add_subscribe.html',mail = mail,url = url)

@app.route('/unsubscribe/<int:observable_id>/<int:subscriber_id>')
def unsubscribe(observable_id,subscriber_id):
    '''
    取消订阅
    :param subscriber_id:
    :param observable_id:
    :return:
    '''
    return jsonify(database.delSubscribeById(subscriber_id,observable_id))

if __name__ == '__main__':
    app.run(debug=True)
