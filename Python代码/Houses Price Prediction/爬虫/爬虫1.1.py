import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import os
import random
import re
import json
from DrissionPage import ChromiumPage
def get_cookie():
    cookies = json.loads(open('cookies.txt').read())
    return cookies
def ccs():
    # 创建一个 Chromium 浏览器页面实例
    page = ChromiumPage()
    dic = {}
    # 打开一个网页
    page.get('https://bj.lianjia.com/chengjiao/chaoyang/pg2/')
    input('完成滑块后:')
    cookiess = page.cookies()
    for i in cookiess:
        dic[i['name']] = i['value']
    print(dic)
    with open('cookies.txt', 'w+') as f:
        f.write(json.dumps(dic))
def kuaidaili():
    tunnel = "o646.kdltps.com:15818"
    username = "t14576732515736"
    password = "bm47ern7"
    proxies = {
        "http": "http://%(user)s:%(pwd)s@%(proxy)s/" % {"user": username, "pwd": password, "proxy": tunnel},
        "https": "http://%(user)s:%(pwd)s@%(proxy)s/" % {"user": username, "pwd": password, "proxy": tunnel}
    }
    return proxies


headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
    'Connection': 'keep-alive',
    'Referer': 'https://bj.lianjia.com/chengjiao/chaoyang/pg1/',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-User': '?1',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36 Edg/135.0.0.0',
    'sec-ch-ua': '"Microsoft Edge";v="135", "Not-A.Brand";v="8", "Chromium";v="135"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    #'Cookie': 'select_city=110000; lianjia_ssid=df10b3fa-0804-4ef5-bc66-ee27e191050f; lianjia_uuid=2e37aa5d-2f0f-4d19-aba7-5da34f856c5f; crosSdkDT2019DeviceId=-gm6cbh--vj7gdi-ga2eu7kqzrkr92z-ra6mu5w04; login_ucid=2000000299810717; lianjia_token=2.00135992187b24406902f4bb29499cf453; lianjia_token_secure=2.00135992187b24406902f4bb29499cf453; security_ticket=FRWLGCrJ9RolnSR0Z4cimmmXK8Zo1Yf+d63daXustnS74JeSMsPQUeZfJbGd79gnjj1cj71U0Bs8F6DrxGgMo70toRqT7smoaQScKgbGAEWzbiE6b5BQZPAk287XyN+ECU50gueeX3um0pAv7tFyutmaM9UOgVWmHYBsQLvXTP8=; ftkrc_=26b5a9a6-c594-46e9-9beb-4b84411d1340; lfrc_=9d787dca-c9d9-4553-a240-a79c8503e8a4; _jzqa=1.2179782629979567600.1745771257.1745771257.1745771257.1; _jzqc=1; _jzqx=1.1745771257.1745771257.1.jzqsr=clogin%2Elianjia%2Ecom|jzqct=/.-; _jzqckmp=1; Hm_lvt_46bf127ac9b856df503ec2dbf942b67e=1745771257; Hm_lpvt_46bf127ac9b856df503ec2dbf942b67e=1745771257; HMACCOUNT=239835E0ADEA658F; _qzja=1.913028438.1745771257497.1745771257497.1745771257497.1745771257497.1745771257497.0.0.0.1.1; _qzjc=1; _qzjto=1.1.0; _jzqb=1.1.10.1745771257.1; sajssdk_2015_cross_new_user=1; sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%2219678135fab15c3-016fd11c7690e9-4c657b58-1474560-19678135fac1921%22%2C%22%24device_id%22%3A%2219678135fab15c3-016fd11c7690e9-4c657b58-1474560-19678135fac1921%22%2C%22props%22%3A%7B%7D%7D; srcid=eyJ0Ijoie1wiZGF0YVwiOlwiZDA5N2U5MGZiZDVhZmQ3ZDQxZDdlY2U0YzUzYzRlMzFjN2Q4ZjcwYTEzODQ5NWFkYzU0NmQzMzE4MjI1MzFjMzQ0MGZmM2MwZmYzNGE2ODgyOGEyMDBkNDE0Y2JlNDRhNTJjMDY2ODA1YTFmN2I1ZTMwYjcyM2EwMWU0ZjIyZDgyZjRhMTRhZDg0ZTIzYzNlZTg2OWUyNzdhYjY5MjY2NWQ0NGYxZTY4MzA3ZWYwZGE3NDNlMzJhNDZjM2NjNDI4NjA0ZTQyOWE0ZWY3NTExNDY4NjdjYjhlODMwMDZjMWFlMWMxNzhkOThkYjkxYjY5MTRjYTlmZDI0OTdmNjhmZFwiLFwia2V5X2lkXCI6XCIxXCIsXCJzaWduXCI6XCI2OTA1M2I3MlwifSIsInIiOiJodHRwczovL2JqLmxpYW5qaWEuY29tL2NoZW5namlhby9jaGFveWFuZy9wZzEvIiwib3MiOiJ3ZWIiLCJ2IjoiMC4xIn0=; _qzjb=1.1745771257497.1.0.0.0; _ga=GA1.2.1741539050.1745771270; _gid=GA1.2.303452653.1745771270; _gat=1; _gat_past=1; _gat_global=1; _gat_new_global=1; _gat_dianpu_agent=1; _ga_KJTRWRHDL1=GS1.2.1745771270.1.0.1745771270.0.0.0; _ga_QJN1VP0CMS=GS1.2.1745771271.1.0.1745771271.0.0.0',
}
start_time = time.time()
def kks(District,index_main_page):
    print(f"https://bj.lianjia.com/chengjiao/{District}/pg{index_main_page}/")
    T = 0
    while True:
        resp1 = requests.get(f"https://bj.lianjia.com/chengjiao/{District}/pg{index_main_page}/", headers=headers,cookies=get_cookie(),
                             proxies=kuaidaili())
        if '本次访问已触发人机验证，请按指示操作' in resp1.text:
            #print(resp1.text)
            T += 1
            if T == 10:
                ccs()
        else:
            return resp1
# 北京的行政区拼音
district_pinyin_list = [
    'chaoyang', 'haidian', 'dongcheng', 'xicheng', 'fengtai',
    'changping', 'daxing', 'fangshan', 'tongzhou', 'shunyi',
    'miyun', 'pinggu', 'huairou', 'yanqing', 'licheng', 'jiuxian',
    'shijingshan', 'changping', 'yizhuang', 'zhongguancun', 'huanan'
]

try:
    # 遍历每个行政区
    for District in district_pinyin_list:
        for index_main_page in range(7, 100):
            try:

                resp1 = kks(District,index_main_page)
                print(resp1.text)
                resp1.raise_for_status()

                # print("主界面链接获取成功")
                resp1.encoding = "utf-8"

                main_page = BeautifulSoup(resp1.text, "html.parser")
                print(f"主界面第{index_main_page}页解析成功...")
                # print(main_page)

                child_list = main_page.find("ul", class_='listContent').find_all('a', class_=re.compile(r'img'))    # 只要 class 属性里有 “img” 字样

                # print(child_list)

                resp1.close()
        ##########################################################################
                index_child_page = 0
                for child in child_list:    # 每一个子页面链接
                    index_child_page += 1
                    print(f"正在爬取第{index_main_page}页第{index_child_page}个子页面..." , end = '')

                    href = child.get('href')
                    print(f"链接：{href}")

                    # 获取子界面数据
                    try:
                        resp2 = requests.get(href, headers=headers,cookies=get_cookie(),proxies=kuaidaili())
                    except Exception as e:
                        try:
                            resp2 = requests.get(href, headers=headers,cookies=get_cookie(), proxies=kuaidaili())
                        except Exception as e:
                            try:
                                resp2 = requests.get(href, headers=headers,cookies=get_cookie(), proxies=kuaidaili())
                            except Exception as e:
                                try:
                                    resp2 = requests.get(href, headers=headers,cookies=get_cookie(), proxies=kuaidaili())
                                except Exception as e:
                                    try:
                                        resp2 = requests.get(href, headers=headers,cookies=get_cookie(), proxies=kuaidaili())
                                    except Exception as e:
                                        with open('异常链接.txt','a+',encoding='utf-8') as f:
                                            f.write(href)
                                            f.write('\n')
                    resp2.raise_for_status()
                    # print("子界面数据获取成功")
                    resp2.encoding = "utf-8"

                    child_page = BeautifulSoup(resp2.text, "html.parser")
                    # print(child_page)

        ##################
                    # 价格
                    try:
                        price = child_page.find("div", class_="msg").find('label').string.strip()
                    except:
                        price = 'Na'

                    # 户型
                    try:
                        house_type = child_page.find("span", class_='label', string='房屋户型').next_sibling.strip()
                    except:
                        house_type = 'Na'

                    # 面积
                    try:
                        area_text = child_page.find('span', class_='label', string='建筑面积').next_sibling.strip()
                        area = re.findall(r'\d+', area_text)[0]  # 提取数字部分
                    except:
                        area = 'Na'

                    # 房屋朝向
                    try:
                        orientation = child_page.find("span", class_='label', string='房屋朝向').next_sibling.strip()
                    except:
                        orientation = 'Na'

                    # 建筑结构
                    try:
                        building_struct = child_page.find("span", class_='label', string='建筑结构').next_sibling.strip()
                    except:
                        building_struct = 'Na'

                    # 户型结构
                    try:
                        house_struct = child_page.find("span", class_='label', string='户型结构').next_sibling.strip()
                    except:
                        house_struct = 'Na'

                    # 建筑类型
                    try:
                        building_type = child_page.find("span", class_='label', string='建筑类型').next_sibling.strip()
                    except:
                        building_type = 'Na'

                    # 装修情况
                    try:
                        decoration = child_page.find("span", class_='label', string='装修情况').next_sibling.strip()
                    except:
                        decoration = 'Na'

                    # 供暖方式
                    try:
                        heating_method = child_page.find("span", class_='label', string='供暖方式').next_sibling.strip()
                    except:
                        heating_method = 'Na'

                    # 电梯
                    try:
                        elevator = child_page.find("span", class_='label', string='配备电梯').next_sibling.strip()
                    except:
                        elevator = 'Na'

        ##################
                    # 链家编号
                    try:
                        number = child_page.find("div", class_='transaction').find("span", class_='label',
                                                                                   string='链家编号').next_sibling.strip()
                    except:
                        number = 'Na'

                    # 房屋年限
                    try:
                        years_of_house = child_page.find("div", class_='transaction').find("span", class_='label',
                                                                                           string='房屋年限').next_sibling.strip()
                    except:
                        years_of_house = 'Na'

                    # 交易权属
                    try:
                        ownership_of_transactions = child_page.find("div", class_='transaction').find("span", class_='label',
                                                                                                      string='交易权属').next_sibling.strip()
                    except:
                        ownership_of_transactions = 'Na'

                    # 房屋用途
                    try:
                        usage_of_house = child_page.find("div", class_='transaction').find("span", class_='label',
                                                                                           string='房屋用途').next_sibling.strip()
                    except:
                        usage_of_house = 'Na'

                    # 房权所属
                    try:
                        ownership_of_house = child_page.find("div", class_='transaction').find("span", class_='label',
                                                                                               string='房权所属').next_sibling.strip()
                    except:
                        ownership_of_house = 'Na'

        #################
                    # 行政区
                    try:
                        region_list = child_page.find("div", class_="deal-bread").find_all('a')
                        district = region_list[2].string[:-5] if len(region_list) > 2 else 'Na'
                    except:
                        district = 'Na'

                    # 街道
                    try:
                        street = region_list[3].string[:-5] if len(region_list) > 3 else 'Na'
                    except:
                        street = 'Na'

                    # 小区
                    try:
                        community = region_list[4].string[:-5] if len(region_list) > 4 else 'Na'
                    except:
                        community = 'Na'

        ##############
                    # 地铁
                    try:
                        subway = 0
                        # 1
                        subway_text = child_page.find("div", class_='introContent showbasemore').find("a").string.strip()
                        if "地铁" in subway_text:
                            subway = 1
                        #print(subway)
                        # print(subway)

                        # 2
                        traffic_div = child_page.find("div", class_="name", string="交通出行")
                        content_text = traffic_div.find_next("div", class_="content").get_text(strip=True)
                        if "地铁" in content_text:
                            subway = 1
                            #print("文本中包含‘地铁’二字")
                    except:
                        subway = '0'
        ################
                    # 经纬度（动态网页，正则表达式）
                    location_pattern = re.compile(r"resblockPosition:\s*'(-?\d+\.\d+),\s*(-?\d+\.\d+)'", re.S)

                    # 使用search方法查找匹配项
                    match = location_pattern.search(resp2.text)

                    if match:
                        longitude = match.group(1)
                        latitude = match.group(2)
                        # print(f"经纬度：{longitude}, {latitude}")
                    else:
                        print("未找到匹配的经纬度信息")

                    resp2.close()
        ###############################################################################
                    # 保存到xlsx文件中
                    data = {
                        '贝壳编号': [number],
                        '价格(万元)': [price],
                        '户型': [house_type],
                        '面积(㎡)': [area],
                        '房屋朝向': [orientation],
                        '建筑结构': [building_struct],
                        '户型结构': [house_struct],
                        '建筑类型': [building_type],
                        '装修情况': [decoration],
                        '供暖方式': [heating_method],
                        '配备电梯': [elevator],
                        '房屋年限': [years_of_house],
                        '交易权属': [ownership_of_transactions],
                        '房屋用途': [usage_of_house],
                        '房权所属': [ownership_of_house],
                        '行政区': [district],
                        '街道': [street],
                        '小区': [community],
                        '地铁': [subway],
                        '经度': [longitude],
                        '纬度': [latitude]
                    }

                    dataframe_name = pd.DataFrame(data)

                    file_path = '/Users/jia/Desktop/学习 /科研/独立论文部分/北京二手房数据(链家)_opitimizaion_1.xlsx'

                    if os.path.exists(file_path):
                        existing_data = pd.read_excel(file_path)
                        dataframe_name = pd.concat([existing_data, dataframe_name], ignore_index=True)

                    dataframe_name.to_excel(file_path, index=False)

                    print('成功下载！----', end='')
                    end_time = time.time()
                    print(
                        f"用时：{round((end_time - start_time) // 60)}分{round((end_time - start_time) % 60)}秒")

                    time.sleep(random.randint(1, 2))
                time.sleep(random.randint(5,6))
            except requests.exceptions.RequestException as e:
                print(f"请求失败，跳过第{index_main_page}页，错误：{e}")
                continue  # 如果请求失败，跳过当前循环，进入下一次循环

            time.sleep(30)
        time.sleep(170)

except requests.exceptions.RequestException as e:
    try:
        resp1.close()
    except:
        pass
    try:
        resp2.close()
    except:
        pass
    print("resp1或resp2已经关闭")
    print(f"{e}获取链接失败")