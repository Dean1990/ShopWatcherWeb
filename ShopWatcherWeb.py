import json

import pymysql
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
    return 'Hello World!'

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
def observable_list():
    observables = database.getObservableAll()
    for obs in observables :
        items = database.getItems(obs.url,-20)
        if items and len(items):
            print(items[0])
            obs.v_item = items[0]
            for item in items:
                if item.min_price != items[0]:
                    obs.v_trend = items[0].min_price - item.min_price
                    break

    return render_template('observable_list.html',list = observables)

@app.route('/item_list/<int:id>')
def item_list(id):
    data = []
    if id:
        observable = database.getObservable(id)
        if observable:
            items = database.getItems(observable.url, 20)
            for item in items:
                data.append(item.jsonStr())
    return jsonify(data);

@app.route('/subscribe',methods=['POST','GET'])
def subscribe():
    if request.method == 'POST':
        mail = request.form['mail']
        url = request.form['url']
        hope_price = request.form['hope_price']
        url = utils.trimUrl(url)
        if mail and url:
            subscriber_id = database.addSubscriber(mail)
            if not hope_price:
                hope_price = 0
            database.subscribe(subscriber_id,url,hope_price)
            observable = database.getObservableByUrl(url)
            if observable:
                observables = []
                observables.append(observable)
                task.classifyCaptureSave(observables)
        else:
            return "邮箱和商品链接不能为空"
        return observable_list()
    else:
        return render_template('subscribe.html')

if __name__ == '__main__':
    app.run(debug=True)
