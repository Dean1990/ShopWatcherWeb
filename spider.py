import requests
from bs4 import BeautifulSoup
import re

from entity import Item


def captureTaobaoItem(url):
    '''网络获取'''
    res = requests.get(url)
    soup = BeautifulSoup(res.text, features='html.parser')
    # title
    title = soup.find('h3', class_='tb-main-title').attrs['data-title'].strip()
    print("spider.captureTaobaoItem >> "+title)
    # price
    price = soup.find('em', class_='tb-rmb-num').text.strip()
    print("spider.captureTaobaoItem >> "+price)
    print("spider.captureTaobaoItem >> "+url)
    item = Item(url, title, 0, 0)
    pattern = re.compile("[\d\.]+")
    match = pattern.findall(price)
    if match:
        item.min_price = match[0]
        if len(match)>1:
            item.max_price = match[1]
    return item