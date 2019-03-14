import datetime
import smtplib
import threading
from email.header import Header
from email.mime.text import MIMEText

# import matplotlib.pyplot as plt
import time

import config
from database import getObservableAll, addItem, getSubscribes, getItems, getSubscriber, getObservableByUrl, \
    getSubscribe, addObservable, addSubscribe, getSubscriberByMail, delSubscribeById, getLabel, updateLabel, \
    updateSubscribe, updateObservable
from spider import captureTaobaoItem
from utils import trimUrl


def subscribe(subscriber_id, url,label_id,hope_price=0):
    '''
    订阅
    :return:
    '''
    url = trimUrl(url)
    if subscriber_id and url and label_id:

            observable = getObservableByUrl(url)
            if observable:
                # 如果存在 去查订阅关系
                sub = getSubscribe(subscriber_id,observable.id)
                if sub :
                    # 该用户已经订阅过
                    print("task.subscribe >> subscriber id:" + str(subscriber_id) + "has subscribed " + url)
                    # 更新期望价格
                    sub.hope_price = hope_price
                    updateSubscribe(sub)
                else:
                    # 订阅
                    addSubscribe(subscriber_id,observable.id,hope_price)
                # 更新标签
                observable.label_id = label_id
                updateObservable(observable)
            else:
                # 先添加到被观察者中，再订阅
                observable = addObservable(url,label_id)
                if observable:
                    # 订阅
                    addSubscribe(subscriber_id, observable.id,hope_price)

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
        subscriber = getSubscriberByMail(mail)
        if subscriber:
            observable = getObservableByUrl(url)
            if observable:
                # 只删除订阅关系即可
                b = delSubscribeById(subscriber.id,observable.id)
    return b

def classifyCaptureSave(observables):
    '''
    归类抓取 并入库
    :return:
    '''
    capture_work = False
    for obs in observables:
        if capture_work:
            time.sleep(5) # 暂停5秒抓取一次
        item = None
        if obs.url.startswith("https://item.taobao.com"):
            item = captureTaobaoItem(obs.url)
            capture_work = True
        # elif
        if item:
            # 保存
            addItem(item)
            if obs.label_id:
                #更新最低价
                label = getLabel(obs.label_id)
                if label:
                    if label.lowest_price == 0 or float(label.lowest_price) > float(item.min_price):
                        label.lowest_price = item.min_price
                        # 保存最低价
                        updateLabel(label)

            # 对比价格
            comparePrice(item,obs.id)


def timedCaptureTask():
    '''
    定时任务 查询订阅 - 抓取 - 解析 - 入库
    :return:
    '''
    print("task.timedCaptureTask >> " + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    try :
        classifyCaptureSave(getObservableAll())
    except Exception as e:
        print(str(e))
        print("timedCaptureTask timer reset")
    timer = threading.Timer(config.capture_interval,timedCaptureTask)
    timer.start()

def comparePrice(item,observable_id):
    '''
    比较价格 发通知
    :param observable_id:
    :return:
    '''
    if item:
        subscribes = getSubscribes(observable_id)
        for sub in subscribes:
            if sub.hope_price:
                # 设置了期望值
                reduction = float(sub.hope_price) - float(item.min_price)
                if reduction>=0:
                    # 发通知
                    subscriber = getSubscriber(sub.subscriber_id)
                    sendMail(subscriber,item,reduction)
            else:
                # 去item表中查倒数第二条
                items = getItems(item.url,-2)
                if items and len(items)==2:
                    reduction = float(items[1].min_price) - float(items[0].min_price)
                    if reduction >= 0:
                        # 发通知
                        subscriber = getSubscriber(sub.subscriber_id)
                        sendMail(subscriber, item, reduction)


# def paintTrend(items):
#     '''
#     画出趋势图
#     :param items:
#     :return:
#     '''
#     if items:
#         flg = plt.figure()
#         ax = flg.add_subplot(111)#在画板的第1行第1列的第一个位置生成
#         ids = []
#         min_prices = []
#         max_prices = []
#
#         for item in items:
#             ids.append(item.id)
#             min_prices.append(item.min_price)
#             max_prices.append(item.max_price)
#         # 计算Y轴范围
#         maxp = int(str(max(max_prices)))
#         minp = int(str(min(min_prices)))
#         if maxp < minp:
#             maxp = int(str(max(min_prices)))
#         offset = int((maxp + minp)**0.5)
#         ax.set(xlim=[0,len(items)],ylim=[minp-offset,maxp+offset],title=item.title,xlabel='Date',ylabel='Price')
#
#         plt.plot(ids,min_prices)
#         plt.plot(ids,max_prices)
#         plt.show()

def sendMail(subscriber,item,reduction):
    '''
    发邮件
    :param subscriber:
    :param item:
    :param reduction: 降价幅度
    :return:
    '''
    if subscriber and item and reduction:
        # 第三方 SMTP 服务
        mail_host = config.mail_config['smtp']  # 设置SMTP服务器 如：smtp.sina.com
        mail_user = config.mail_config['user']  # 用户名
        mail_pass = config.mail_config['passwd']  # 密码

        sender = config.mail_config['user']
        # receivers = [subscriber.mail] # 接收邮件地址
        receivers = [subscriber.mail] # 接收邮件地址

        # 三个参数：第一个为文本内容，第二个 plain 设置文本格式，第三个 utf-8 设置编码
        mail_msg = "<span>您关注的商品 <b>["+item.title+"]</b> 比关注时降价 <font color='red' ><b>" + str(reduction) + "</b></font> 元</span></br><span>商品链接：<a href='"+item.url+"'>"+item.url+"</a></span>"
        message = MIMEText( mail_msg ,'html','utf-8') # 内容
        message['From'] = Header(sender) # 发送者
        message['To'] = Header(subscriber.name if subscriber.name else subscriber.mail ,'utf-8') # 接收者

        subject = '[降价通知]' + item.title
        message['Subject'] = Header(subject,'utf-8') # 标题

        try:
            smtpObj = smtplib.SMTP()
            smtpObj.connect(mail_host,25)
            smtpObj.login(mail_user,mail_pass)
            smtpObj.sendmail(sender,receivers,message.as_string())
            smtpObj.quit()
            print("task.sendMail >> Email sent successfully")
        except Exception as e:
            print("task.sendMail >> " + e)
            print("task.sendMail >> Error:Unable to send message")

def sendSMS(subscriber,item,reduction):
    '''
    发短信
    :param subscriber:
    :param item:
    :param reduction:
    :return:
    '''
    print('They charge a fee')