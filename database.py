import pymysql

import config
from entity import Item, Observable, Subscribe, Subscriber
from utils import trimUrl


def initDatabase():
    '''
    初始化数据库
    :return:
    '''
    db = pymysql.connect(config.database_config['host'], config.database_config['user'], config.database_config['passwd'], config.database_config['db_name'])
    cursor = db.cursor()
    item_sql = "CREATE TABLE IF NOT EXISTS `item` (`id` int(11) NOT NULL AUTO_INCREMENT,`url` varchar(255) NOT NULL,`title` varchar(255) DEFAULT NULL,`min_price` decimal(10,0) NOT NULL,`max_price` decimal(10,0) DEFAULT NULL,`date` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,PRIMARY KEY (`id`)) ENGINE=InnoDB DEFAULT CHARSET=utf8;"
    observable_sql = "CREATE TABLE IF NOT EXISTS `observable` (`id` int(11) NOT NULL AUTO_INCREMENT,`url` varchar(255) NOT NULL,`date` timestamp NULL DEFAULT CURRENT_TIMESTAMP,PRIMARY KEY (`id`)) ENGINE=InnoDB DEFAULT CHARSET=utf8;"
    subscribe_sql = "CREATE TABLE IF NOT EXISTS `subscribe` (`id` int(11) NOT NULL AUTO_INCREMENT,`subscriber_id` int(11) NOT NULL,`observable_id` int(11) NOT NULL,`hope_price` decimal(10,0) DEFAULT NULL,`date` timestamp NULL DEFAULT CURRENT_TIMESTAMP,PRIMARY KEY (`id`)) ENGINE=InnoDB DEFAULT CHARSET=utf8;"
    subscriber_sql = "CREATE TABLE IF NOT EXISTS `subscriber` (`id` int(11) NOT NULL AUTO_INCREMENT,`name` varchar(255) DEFAULT NULL,`phone` varchar(255) DEFAULT NULL,`mail` varchar(255) NOT NULL,`date` timestamp NULL DEFAULT CURRENT_TIMESTAMP,PRIMARY KEY (`id`)) ENGINE=InnoDB DEFAULT CHARSET=utf8;"
    try:
        print("database.initDatabase >> " + item_sql)
        cursor.execute(item_sql)
        print("database.initDatabase >> " + observable_sql)
        cursor.execute(observable_sql)
        print("database.initDatabase >> " + subscribe_sql)
        cursor.execute(subscribe_sql)
        print("database.initDatabase >> " + subscriber_sql)
        cursor.execute(subscriber_sql)
        db.commit()
    except:
        db.rollback()
    db.close()


def saveItem(item):
    '''
    保存到数据库
    :param item:
    :return:
    '''
    if item:
        db = pymysql.connect(config.database_config['host'], config.database_config['user'], config.database_config['passwd'], config.database_config['db_name'])
        cursor = db.cursor()
        sql = "insert into item(url,title,min_price,max_price) values('" + item.url + "','" + item.title + "'," + item.min_price + "," + item.max_price + ")"
        print("database.saveItem >> " + sql)
        try:
            cursor.execute(sql)
            db.commit()
        except:
            db.rollback()
        db.close()


def getItems(url, limit=0):
    '''
    从数据库查询
    :param url:
    :param limit 支持倒数
    :return: item []
    '''
    items = []
    url = trimUrl(url)
    if url:
        db = pymysql.connect(config.database_config['host'], config.database_config['user'], config.database_config['passwd'], config.database_config['db_name'])
        cursor = db.cursor()
        ext = ""
        if limit:
            order = ""
            if limit < 0:
                order = "desc"
            ext = " order by date " + order + " limit " + str(abs(limit))
        sql = "select * from item where url = '" + url + "'" + ext
        print("database.getItems >> " + sql)
        try:
            cursor.execute(sql)
            results = cursor.fetchall()
            for row in results:
                item = Item(row[1], row[2], row[3], row[4])
                item.id = row[0]
                item.date = row[5]
                items.append(item)
        except:
            print("database.getItems >> Error: unable to fetch data")
        db.close()
    return items


def addSubscriber(mail,phone = "", name=""):
    '''
    增加订阅者
    :return: 新增订阅者的ID str
    '''
    if mail:
        db = pymysql.connect(config.database_config['host'], config.database_config['user'], config.database_config['passwd'], config.database_config['db_name'])
        cursor = db.cursor()
        select_sql = "select * from subscriber where mail = '" + mail + "'"
        print("database.addSubscriber >> " + select_sql)
        try:
            cursor.execute(select_sql)
            results = cursor.fetchall()
            sql = ""
            if results and len(results):
                # 存在
                if not phone :
                    phone = results[0][2]
                sql = "update subscriber set phone = '" + phone + "', mail = '" + mail + "', name = '" + name + "' where id = " + str(
                    results[0][0])
                print("database.addSubscriber >> " + sql)
            else:
                sql = "insert into subscriber(phone,mail,name) values('" + phone + "','" + mail + "','" + name + "')"
            print("database.addSubscriber >> " + sql)
            cursor.execute(sql)
            db.commit()
            cursor.execute(select_sql)
            results = cursor.fetchall()
            if results and len(results):
                return str(results[0][0])
        except Exception as e:
            print("database.addSubscriber >> " + e)
            db.rollback()
        db.close()

def getObservableByUrl(url):
    observable = None
    db = pymysql.connect(config.database_config['host'], config.database_config['user'],
                         config.database_config['passwd'], config.database_config['db_name'])
    cursor = db.cursor()
    sql = "select * from observable where url = '" + url + "'"
    print("database.getObservableByUrl >> " + sql)
    try:
        cursor.execute(sql)
        results = cursor.fetchall()
        if results and len(results):
            observable = Observable(results[0][0], results[0][1], results[0][2])
    except:
        print("database.getObservableByUrl >> Error: unable to fetch data")
    db.close()
    return observable

def subscribe(subscriber_id, url, hope_price=0):
    '''
    订阅
    :return:
    '''
    url = trimUrl(url)
    if subscriber_id and url:
        db = pymysql.connect(config.database_config['host'], config.database_config['user'], config.database_config['passwd'], config.database_config['db_name'])
        cursor = db.cursor()
        sql = "select * from observable where url = '" + url + "'"
        print("database.subscribe >> " + sql)
        try:
            cursor.execute(sql)
            results = cursor.fetchall()
            if results and len(results):
                # 如果存在 去查订阅关系
                obs_id = str(results[0][0])
                sql = "select * from subscribe where subscriber_id = " + subscriber_id + " and observable_id = " + obs_id
                cursor.execute(sql)
                results = cursor.fetchall()
                if results and len(results):
                    # 该用户已经订阅过
                    print("database.subscribe >> subscriber id:" + str(subscriber_id) + "has subscribed " + url)
                else:
                    # 订阅
                    sql = "insert into subscribe(subscriber_id,observable_id,hope_price) values(" + subscriber_id + "," + obs_id + "," + str(hope_price) + ")"
                    cursor.execute(sql)
                    db.commit()
            else:
                # 先添加到被观察者中，再订阅
                sql = "insert into observable(url) values('" + url + "')"
                print("database.subscribe >> " + sql)
                cursor.execute(sql)
                db.commit()
                # 查询出ID
                sql = "select * from observable where url = '" + url + "'"
                print("database.subscribe >> " + sql)
                cursor.execute(sql)
                results = cursor.fetchall()
                if results and len(results):
                    obs_id = str(results[0][0])
                    # 订阅
                    sql = "insert into subscribe(subscriber_id,observable_id,hope_price) values(" + subscriber_id + "," + obs_id + "," + str(hope_price) + ")"
                    cursor.execute(sql)
                    db.commit()
        except Exception as e:
            print("database.subscribe >> " + e)
            db.rollback()
        db.close()

def getObservable(id):
    '''
    查询被观察者
    :param id:
    :return:
    '''
    observable = None
    db = pymysql.connect(config.database_config['host'], config.database_config['user'],
                         config.database_config['passwd'], config.database_config['db_name'])
    cursor = db.cursor()
    sql = "select * from observable where id = " + str(id)
    try:
        cursor.execute(sql)
        results = cursor.fetchall()
        if results and len(results):
            observable = Observable(results[0][0],results[0][1],results[0][2])
    except:
        print("database.getObservable >> Error: unable to fetch data")
    db.close()
    return observable

def getObservableAll():
    '''
    查询所有的被观察者
    :return: Observable []
    '''
    observables = []
    db = pymysql.connect(config.database_config['host'], config.database_config['user'], config.database_config['passwd'], config.database_config['db_name'])
    cursor = db.cursor()
    sql = "select * from observable"
    try:
        cursor.execute(sql)
        results = cursor.fetchall()
        for row in results:
            observable = Observable(row[0], row[1], row[2])
            observables.append(observable)
    except:
        print("database.getObservableAll >> Error: unable to fetch data")
    db.close()
    return observables


def getSubscribes(observable_id):
    '''
    查询指定 observable id 的所有订阅
    :param observable_id:
    :return: Subscribe []
    '''
    subscribes = []
    if observable_id:
        db = pymysql.connect(config.database_config['host'], config.database_config['user'], config.database_config['passwd'], config.database_config['db_name'])
        cursor = db.cursor()
        sql = "select * from subscribe where observable_id = " + str(observable_id)
        print("database.getSubscribes >> " + sql)
        try:
            cursor.execute(sql)
            results = cursor.fetchall()
            for row in results:
                subscribe = Subscribe(row[0], row[1], row[2], row[3], row[4])
                subscribes.append(subscribe)
        except Exception as e:
            print("database.getSubscribes >> "+e)
            print("database.getSubscribes >> Error: unable to fetch data")
        db.close()
    return subscribes


def getSubscriber(id):
    '''
    查询订阅者
    :param id:
    :return: Subscriber
    '''
    subscriber = None
    if id:
        db = pymysql.connect(config.database_config['host'], config.database_config['user'], config.database_config['passwd'], config.database_config['db_name'])
        cursor = db.cursor()
        sql = "select * from subscriber where id = " + str(id)
        print("database.getSubscriber >> " + sql)
        try:
            cursor.execute(sql)
            results = cursor.fetchall()
            if results and len(results):
                subscriber = Subscriber(results[0][0], results[0][1], results[0][2], results[0][3], results[0][4])
        except:
            print("database.getSubscriber >> Error: unable to fetch data")
        db.close()
    return subscriber

def unsubscribeById(subscriber_id,observable_id):
    b = False
    db = pymysql.connect(config.database_config['host'], config.database_config['user'],
                         config.database_config['passwd'], config.database_config['db_name'])
    cursor = db.cursor()
    sql = "delete from subscribe where subscriber_id = " + str(subscriber_id) + " and observable_id = " + str(
        observable_id)
    print("database.unsubscribe >> " + sql)
    try:
        cursor.execute(sql)
        db.commit()
        b = True
    except Exception as e:
        print("database.unsubscribe >> " + e)
        db.rollback()
    db.close()
    return b

def unsubscribe(url,mail):
    '''
    取消订阅
    :param url:
    :param mail:
    :return:
    '''
    b = False
    url = trimUrl(url)
    if url and mail:
        db = pymysql.connect(config.database_config['host'], config.database_config['user'],
                             config.database_config['passwd'], config.database_config['db_name'])
        cursor = db.cursor()
        sql = "select * from subscriber where mail = " + mail
        print("database.unsubscribe >> " + sql)
        try:
            cursor.execute(sql)
            results = cursor.fetchall()
            if results and len(results):
                subscriber_id = results[0][0]
                sql = "select * from observable where url = " + url
                print("database.unsubscribe >> " + sql)
                cursor.execute(sql)
                results = cursor.fetchall()
                if results and len(results):
                    observable_id = results[0][0]
                    # 只删除订阅关系即可
                    sql = "delete from subscribe where subscriber_id = "+str(subscriber_id) +" and observable_id = " + str(observable_id)
                    print("database.unsubscribe >> " + sql)
                    cursor.execute(sql)
                    db.commit()
                    b = True
        except Exception as e:
            print("database.unsubscribe >> " + e)
            db.rollback()
        db.close()
        return b

def isSubscribe(subscriber_id,observable_id):
    '''
    是否订阅
    :param subscriber_id:
    :param observable_id:
    :return:
    '''
    b = False
    db = pymysql.connect(config.database_config['host'], config.database_config['user'],
                         config.database_config['passwd'], config.database_config['db_name'])
    cursor = db.cursor()
    sql = 'select * from subscribe where subscriber_id = ' + str(subscriber_id) + ' and observable_id = ' + str(observable_id)
    print("database.isSubscribe >> " + sql)
    try:
        results = cursor.execute(sql)
        b = results > 0
    except Exception as e:
        print("database.isSubscribe >> " + str(e))
    db.close()
    return b