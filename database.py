import pymysql

import config
from entity import Item, Observable, Subscribe, Subscriber, Label
from utils import trimUrl


def initDatabase():
    '''
    初始化数据库
    :return:
    '''
    db = pymysql.connect(config.database_config['host'], config.database_config['user'], config.database_config['passwd'], config.database_config['db_name'])
    cursor = db.cursor()
    item_sql = "CREATE TABLE IF NOT EXISTS `item` (`id` int(11) NOT NULL AUTO_INCREMENT,`url` varchar(255) NOT NULL,`title` varchar(255) DEFAULT NULL,`min_price` decimal(10,2) NOT NULL,`max_price` decimal(10,2) DEFAULT '0.00',`date` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,PRIMARY KEY (`id`)) ENGINE=InnoDB DEFAULT CHARSET=utf8;"
    observable_sql = "CREATE TABLE IF NOT EXISTS `observable` (`id` int(11) NOT NULL AUTO_INCREMENT,`url` varchar(255) NOT NULL,`date` timestamp NULL DEFAULT CURRENT_TIMESTAMP,`lowest_price` decimal(10,2) DEFAULT '0.00',`label_id` int(11) DEFAULT NULL,PRIMARY KEY (`id`)) ENGINE=InnoDB DEFAULT CHARSET=utf8;"
    subscribe_sql = "CREATE TABLE IF NOT EXISTS `subscribe` (`id` int(11) NOT NULL AUTO_INCREMENT,`subscriber_id` int(11) NOT NULL,`observable_id` int(11) NOT NULL,`hope_price` decimal(10,2) DEFAULT NULL,`date` timestamp NULL DEFAULT CURRENT_TIMESTAMP,PRIMARY KEY (`id`)) ENGINE=InnoDB DEFAULT CHARSET=utf8;"
    subscriber_sql = "CREATE TABLE IF NOT EXISTS `subscriber` (`id` int(11) NOT NULL AUTO_INCREMENT,`name` varchar(255) DEFAULT NULL,`phone` varchar(255) DEFAULT NULL,`mail` varchar(255) NOT NULL,`date` timestamp NULL DEFAULT CURRENT_TIMESTAMP,PRIMARY KEY (`id`)) ENGINE=InnoDB DEFAULT CHARSET=utf8;"
    clazz_sql = "CREATE TABLE IF NOT EXISTS `label` (`id` int(11) NOT NULL AUTO_INCREMENT,`name` varchar(255) DEFAULT NULL,`date` timestamp NULL DEFAULT CURRENT_TIMESTAMP,PRIMARY KEY (`id`) ENGINE=InnoDB DEFAULT CHARSET=utf8;"
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


def addItem(item):
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
    :return: 新增订阅者
    '''
    subscriber = None
    if mail:
        db = pymysql.connect(config.database_config['host'], config.database_config['user'], config.database_config['passwd'], config.database_config['db_name'])
        cursor = db.cursor()
        try:
            sql = ""
            subscriber = getSubscriberByMail(mail)
            if subscriber:
                # 存在
                if not phone :
                    phone = subscriber.phone
                if not name :
                    name = subscriber.name
                sql = "update subscriber set phone = '" + phone + "', mail = '" + mail + "', name = '" + name + "' where id = " + str(
                    subscriber.id)
                print("database.addSubscriber >> " + sql)
            else:
                sql = "insert into subscriber(phone,mail,name) values('" + phone + "','" + mail + "','" + name + "')"
            print("database.addSubscriber >> " + sql)
            cursor.execute(sql)
            db.commit()
            subscriber = getSubscriberByMail(mail)

        except Exception as e:
            print("database.addSubscriber >> " + e)
            db.rollback()
        db.close()
    return subscriber

def updateObservable(observable):
    '''
    更新 被观察者
    :param observable:
    :return:
    '''
    b = False
    if observable and observable.id:
        db = pymysql.connect(config.database_config['host'], config.database_config['user'],
                             config.database_config['passwd'], config.database_config['db_name'])
        cursor = db.cursor()
        sql = "update observable set url = '" + observable.url + "',lowest_price = " + str(observable.lowest_price) +" where id = " + str(observable.id)
        print("database.updateObservable >> " + sql)
        try :
            cursor.execute(sql)
            db.commit()
            b = True
        except Exception as e:
            print("database.updateObservable >> "  + str(e))
            db.rollback()
        db.close()
    return b
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
            observable = Observable(results[0][0], results[0][1], results[0][2],results[0][3])
    except:
        print("database.getObservableByUrl >> Error: unable to fetch data")
    db.close()
    return observable

def addObservable(url,lowest_price = 0):
    '''
    添加被观察者
    :param url:
    :param lowest_price:
    :return:
    '''
    url = trimUrl(url)
    if url:
        db = pymysql.connect(config.database_config['host'], config.database_config['user'],
                             config.database_config['passwd'], config.database_config['db_name'])
        cursor = db.cursor()
        try:
            sql = "insert into observable(url,lowest_price) values('" + url + "',"+ str(lowest_price)+" )"
            print("database.subscribe >> " + sql)
            cursor.execute(sql)
            db.commit()
        except Exception as e:
            print("database.subscribe >> " + e)
            db.rollback()
        db.close()

def updateSubscribe(subscribe):
    '''
    更新订阅关系
    :param subscribe:
    :return:
    '''
    b = False
    if subscribe and subscribe.id:
        db = pymysql.connect(config.database_config['host'], config.database_config['user'],
                             config.database_config['passwd'], config.database_config['db_name'])
        cursor = db.cursor()
        sql = "update subscribe set subscriber_id = " + str(subscribe.subscriber_id) + ",observable_id = " + \
              str(subscribe.observable_id) + ",hope_price = " + str(subscribe.hope_price) + " where id = " + str(subscribe.id)
        print("database.updateSubscribe >> " + sql)
        try:
            cursor.execute(sql)
            db.commit()
            b = True
        except Exception as e:
            print("database.updateSubscribe >> " + e)
            db.rollback()
        db.close()
    return b

def addSubscribe(subscriber_id,observable_id,hope_price):
    '''
    订阅
    :param subscriber_id:
    :param observable_id:
    :param hope_price:
    :return:
    '''
    if subscriber_id and observable_id:
        db = pymysql.connect(config.database_config['host'], config.database_config['user'],
                             config.database_config['passwd'], config.database_config['db_name'])
        cursor = db.cursor()
        sql = "insert into subscribe(subscriber_id,observable_id,hope_price) values(" + str(subscriber_id) + "," + str(
            observable_id) + "," + str(hope_price) + ")"
        print("database.addSubscribe >> " + sql)
        try:
            cursor.execute(sql)
            db.commit()
        except Exception as e:
            print("database.addSubscribe >> " + e)
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
            observable = Observable(results[0][0],results[0][1],results[0][2],results[0][3])
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
            observable = Observable(row[0], row[1], row[2],row[3])
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

def getSubscriberByMail(mail):
    subscriber = None
    if mail:
        db = pymysql.connect(config.database_config['host'], config.database_config['user'],
                             config.database_config['passwd'], config.database_config['db_name'])
        cursor = db.cursor()
        select_sql = "select * from subscriber where mail = '" + mail + "'"
        print("database.getSubscriberByMail >> " + select_sql)
        try:
            cursor.execute(select_sql)
            results = cursor.fetchall()
            if results and len(results):
                subscriber = Subscriber(results[0][0], results[0][1], results[0][2], results[0][3], results[0][4])
        except:
            print("database.getSubscriberByMail >> Error: unable to fetch data")
        db.close()
    return subscriber

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

def delSubscribeById(subscriber_id,observable_id):
    '''
    删除订阅关系
    :param subscriber_id:
    :param observable_id:
    :return:
    '''
    b = False
    db = pymysql.connect(config.database_config['host'], config.database_config['user'],
                         config.database_config['passwd'], config.database_config['db_name'])
    cursor = db.cursor()
    sql = "delete from subscribe where subscriber_id = " + str(subscriber_id) + " and observable_id = " + str(
        observable_id)
    print("database.delSubscribeById >> " + sql)
    try:
        result = cursor.execute(sql)
        db.commit()
        b = result > 0
    except Exception as e:
        print("database.delSubscribeById >> " + e)
        db.rollback()
    db.close()
    return b

def getSubscribe(subscriber_id,observable_id):
    '''
    获取订阅
    :param subscriber_id:
    :param observable_id:
    :return:
    '''
    subscribe = None
    db = pymysql.connect(config.database_config['host'], config.database_config['user'],
                         config.database_config['passwd'], config.database_config['db_name'])
    cursor = db.cursor()
    sql = 'select * from subscribe where subscriber_id = ' + str(subscriber_id) + ' and observable_id = ' + str(observable_id)
    print("database.getSubscribe >> " + sql)
    try:
        cursor.execute(sql)
        results = cursor.fetchall()
        if results and len(results):
            subscribe = Subscribe(results[0][0],results[0][1],results[0][2],results[0][3],results[0][4])
    except Exception as e:
        print("database.getSubscribe >> " + str(e))
    db.close()
    return subscribe

def getLabel(id):
    '''
    查询标签
    :param id:
    :return: label
    '''
    label = None
    if id:
        db = pymysql.connect(config.database_config['host'], config.database_config['user'],
                             config.database_config['passwd'], config.database_config['db_name'])
        cursor = db.cursor()
        sql = 'select * from label where id = '+str(id)
        print("database.getLabel >> " + sql)
        try:
            cursor.execute(sql)
            results = cursor.fetchall()
            if results and len(results):
                label = Label(results[0][0],results[0][1],results[0][2])
        except Exception as e:
            print("database.getLabel >> " + str(e))
        db.close()
    return label

def getLabelByName(name):
    '''
    查询标签
    :param name:
    :return: label
    '''
    label = None
    if name:
        db = pymysql.connect(config.database_config['host'], config.database_config['user'],
                             config.database_config['passwd'], config.database_config['db_name'])
        cursor = db.cursor()
        sql = 'select * from label where name = '+name
        print("database.getLabelByName >> " + sql)
        try:
            cursor.execute(sql)
            results = cursor.fetchall()
            if results and len(results):
                label = Label(results[0][0],results[0][1],results[0][2])
        except Exception as e:
            print("database.getLabelByName >> " + str(e))
        db.close()
    return label

def getLabelByLikeName(name):
    '''
    查询标签 模糊查询
    :param name:
    :return: label []
    '''
    clazzs = []
    if name:
        db = pymysql.connect(config.database_config['host'], config.database_config['user'],
                             config.database_config['passwd'], config.database_config['db_name'])
        cursor = db.cursor()
        sql = 'select * from label where name like %'+name + '%'
        print("database.getLabelByLikeName >> " + sql)
        try:
            cursor.execute(sql)
            results = cursor.fetchall()
            for row in results:
                clazzs.append(Label(row[0],row[1],row[2]))
        except Exception as e:
            print("database.getLabelByLikeName >> " + str(e))
        db.close()
    return clazzs

def addLabel(name):
    '''
    增加标签
    :param name:
    :return: label
    '''
    label = getLabelByName(name)
    if not label :
        db = pymysql.connect(config.database_config['host'], config.database_config['user'],
                             config.database_config['passwd'], config.database_config['db_name'])
        cursor = db.cursor()
        sql = 'insert into label(name) values("'+name+'")'
        print("database.addLabel >> " + sql)
        try:
            cursor.execute(sql)
            db.commit()
            label = getLabelByName(name)
        except Exception as e:
            print("database.addLabel >> " + str(e))
            db.rollback()
        db.close()
    return label

def getLabelAll():
    '''
    查询全部标签
    :param name:
    :return: label []
    '''
    clazzs = []
    db = pymysql.connect(config.database_config['host'], config.database_config['user'],
                         config.database_config['passwd'], config.database_config['db_name'])
    cursor = db.cursor()
    sql = 'select * from label'
    print("database.getLabelAll >> " + sql)
    try:
        cursor.execute(sql)
        results = cursor.fetchall()
        for row in results:
            clazzs.append(Label(row[0],row[1],row[2]))
    except Exception as e:
        print("database.getLabelAll >> " + str(e))
    db.close()
    return clazzs