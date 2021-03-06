import json

class Item:
    url = ''
    title = ''
    min_price = 0
    max_price = 0

    id = 0
    date = None

    def __init__(self, url, title, min_price, max_price):
        self.url = url
        self.title = title
        self.min_price = min_price
        self.max_price = max_price

    def __str__(self):
        return "Item["+str(self.id)+","+self.url+","+self.title+","+str(self.min_price)+","+str(self.max_price)+","+str(self.date)+"]"


    def jsonStr(self):
        return json.dumps({
            'id':self.id,
            'date':str(self.date),
            'url':self.url,
            'title':self.title,
            'min_price':float(self.min_price),
            'max_price':float(self.max_price)
        })
        # return "{'id':"+str(self.id)+",'url':'"+self.url+"','title':'"+self.title+"','min_price':"+str(self.min_price)+",'max_price':"+str(self.max_price)+",'date':"+str(self.date)+"}"

class Observable:

    id = 0
    url = ''
    label_id = 0
    date = None


    v_item = None
    v_trend = 0 #用于标记是涨是跌 正数为涨，负数为跌
    v_subscribe = None
    v_label = None

    def __init__(self,id,url,label_id,date):
        self.url = url
        self.id = id
        self.label_id = label_id
        self.date = date


    def __str__(self):
        return "Observable["+str(self.id)+","+self.url+","+str(self.date)+"]"

class Subscribe:
    id = 0

    subscriber_id = 0
    observable_id = 0
    hope_price = 0
    date = None

    def __init__(self, id, subscriber_id, observable_id, hope_price, date):
        self.id = id
        self.subscriber_id = subscriber_id
        self.observable_id = observable_id
        self.hope_price = hope_price
        self.date = date

    def __str__(self):
        return "Subscribe[" + str(self.id) + "," + self.subscriber_id + "," + self.observable_id + "," \
               + self.hope_price + "," + str(self.date) + "]"

class Subscriber:
    id = 0
    date = None

    name =''
    phone =''
    mail =''

    def __init__(self,id,name,phone,mail,date):
        self.id = id
        self.name = name
        self.phone = phone
        self.mail = mail
        self.date = date

    def __str__(self):
        return "Subscriber["+str(self.id)+","+self.name+","+self.phone+","+self.mail+","+str(self.date)+"]"

class Label:
    id = 0
    name = ''
    lowest_price = 0 # 历史最低价
    date = None

    v_min_pirce =0 # 当前最低价
    v_trend = 0 #用于标记是涨是跌 正数为涨，负数为跌

    def __init__(self,id,name,lowest_price,date):
        self.id = id
        self.name = name
        self.lowest_price = lowest_price
        self.date = date

    def __str__(self):
        return "Label["+str(self.id)+","+self.name+","+str(self.date)+"]"