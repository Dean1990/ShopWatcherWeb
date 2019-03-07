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
        # elif