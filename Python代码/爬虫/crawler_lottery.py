"""
1：发送请求头headers
    cookies: 登录后获取的cookies
    user-agent:伪装成浏览器访问
    referer: 登录页面的url(告诉浏览器你的来路)
    host：服务器的域名

    请求方式
        GET/POST
2.获取数据
    respone.text: 页面源码
    response.json：字典码
    response.content：字节码
3.解析数据
    正则表达式
    BeautifulSoup
"""
"""
在页面的network找到所需数据的字典形式（搜索）
查看所需参数的请求头headers。URL如果太长，可以删除?后面，创建一个请求参数字典，在requests是作为参数传入
    可以加入防盗链参数refferrer，防止被网站识别为爬虫
"""

import requests
import re
from bs4 import BeautifulSoup
import pprint
import json

URL = "https://jc.zhcw.com/port/client_json.php"
params = { # 请求参数字典,在负载
    #正则表达式替换 (.*?): (.*)  为  "$1":"$2",
    "callback":"jQuery1122009261594925408279_1720086746548",
    "transactionType":"10001001",
    "lotteryId":"1",
    "issueCount":"0",
    "startIssue":"0",
    "endIssue":"0",
    "startDate":"2020-01-01",
    "endDate":"2021-01-01",
    "type":"2",
    "pageNum":"1",
    "pageSize":"30",
    "tt":"0.516356013850622",
    "_":"1720086746550",
}

headers = { # 请求头headers
    #"cookie":"PHPSESSID=pd1utpb7n4lmriqk0qbftka423; Hm_lvt_692bd5f9c07d3ebd0063062fb0d7622f=1720066659; Hm_lvt_12e4883fd1649d006e3ae22a39f97330=1720066659; _gid=GA1.2.1079975971.1720066659; _ga_9FDP3NWFMS=GS1.1.1720086216.2.1.1720086746.0.0.0; _ga=GA1.1.311841291.1720066659; Hm_lpvt_12e4883fd1649d006e3ae22a39f97330=1720086747; Hm_lpvt_692bd5f9c07d3ebd0063062fb0d7622f=1720086747",
    "referer":"https://jc.zhcw.com/login.php",
    "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0"
}

try:
    response = requests.get(URL, params=params, headers=headers) # 发送请求
    response.raise_for_status() # 状态码检查
    response.encoding = "utf-8"
    pprint.pprint(response.text)
    #pprint.pprint(response.json())
    soup = BeautifulSoup(response.text, "html.parser") # 解析数据
    print(soup.prettify())

except Exception as e:
    print(f"失败！{e}")