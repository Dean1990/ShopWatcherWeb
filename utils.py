import re


def trimUrl(url):
    '''
    梳理url 提取需要的信息
    :param url: 
    :return: 
    '''
    if url:
        if url.startswith("https://item.taobao.com"):
            pattern = re.compile("(https:\/\/item\.taobao\.com\/item\.htm\?).*?(id=\d+)")
            match = pattern.findall(url)
            if match and len(match)==1 and len(match[0])==2:
                return match[0][0] + match[0][1]
        # 天猫的商品抓不到价格，需要使用模拟网页的方式 以后再说
        elif url.startswith("https://detail.tmall.com"):
            pattern = re.compile("(https:\/\/detail\.tmall\.com\/item\.htm\?).*?(id=\d+)")
            match = pattern.findall(url)
            if match and len(match) == 1 and len(match[0]) == 2:
                return match[0][0] + match[0][1]

def obs_cmp(obs, other):
    '''
    被监视者相对于v_subscribe(是否订阅)的比较方法
    :param obs:
    :param other:
    :return:
    '''
    if obs.v_subscribe and other.v_subscribe:
        return 0
    elif obs.v_subscribe:
        return -1
    else:
        return 1