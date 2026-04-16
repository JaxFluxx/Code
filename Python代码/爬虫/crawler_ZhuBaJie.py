from lxml import etree
import requests
import time
import re

headers = {
    "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0"
}

try:
    resp = requests.get("https://www.zbj.com/fw/?k=%E8%BD%AF%E4%BB%B6%E5%BC%80%E5%8F%91", headers=headers)
    resp.raise_for_status()
    print("请求成功!")
except requests.exceptions.RequestException as e:
    print("{e}}请求失败!")


tree = etree.HTML(resp.text)    # resp.text是html，etree是解析html成树方便后续查找
results = tree.xpath('//*[@id="__layout"]/div/div[3]/div[1]/div[4]/div/div[2]/div/div[2]/div')   #找到第一家商家，记得把最后一个dic下标删除

for result in results:  # 遍历第一家商家的所有信息
    price = result.xpath('.//div[1]/div[3]/div[1]/span/text()')[0].strip("¥")   # 找到商家名称,[0]表示取result列表的全部字符串
    name = "".join(result.xpath('.//div[1]/div[3]/div[2]/a/span/text()')[:])   # "".join()把列表里的字符串拼接成一个字符串,因为查找的软件开发被高亮，源码中用<h1></h1>包裹，所以用[:],表示取全部字符串包围起来了

    companys_primitive =result.xpath('.//div/div[5]/div/div/div/text()')[0]   # 找到商家公司名称
    pattern = r'^(.+?)(?=-|$)'
    matches = re.findall(pattern, companys_primitive, re.MULTILINE)
    companys = list(filter(None, matches))  # 去除空字符串
    companys = list(dict.fromkeys(companys))  # 去除重复的公司名称

    print(name)
    print(price)
    print(companys[0])
    print()

test = resp.close()   # 关闭请求