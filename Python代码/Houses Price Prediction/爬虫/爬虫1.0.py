import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import os
import random
import re



headers = {
    "User-Agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0",
    "cookie" : 'lianjia_uuid=62356076-6414-4812-9306-dd21f8eb91ae; crosSdkDT2019DeviceId=vgfd07--obqmlk-oudmek7rz6350ds-xjr1ry073; lfrc_=00873138-ccfb-421b-bc87-262e38d3fc50; sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%221966c6698691323-08a27b37c88d32-7e433c49-3686400-1966c66986afb4%22%2C%22%24device_id%22%3A%221966c6698691323-08a27b37c88d32-7e433c49-3686400-1966c66986afb4%22%2C%22props%22%3A%7B%22%24latest_traffic_source_type%22%3A%22%E7%9B%B4%E6%8E%A5%E6%B5%81%E9%87%8F%22%2C%22%24latest_referrer%22%3A%22%22%2C%22%24latest_referrer_host%22%3A%22%22%2C%22%24latest_search_keyword%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC_%E7%9B%B4%E6%8E%A5%E6%89%93%E5%BC%80%22%2C%22%24latest_utm_source%22%3A%22biying%22%2C%22%24latest_utm_medium%22%3A%22pinzhuan%22%2C%22%24latest_utm_campaign%22%3A%22wybeijing%22%2C%22%24latest_utm_content%22%3A%22biaotimiaoshu%22%2C%22%24latest_utm_term%22%3A%22biaoti%22%7D%7D; lianjia_ssid=e0b5976e-ddac-483e-91c3-7614568143d5; login_ucid=2000000476825870; security_ticket=LCN/xQ0J0WTL38MHgvM467tt6kwio8DPhLOgBFrTzN+sOKsyT/P1BkJm5hv/PZevh1n1R91F3uQ8lowRPe/ieMbOaxE1AHNdAACGthZ55KSkQGq2PQWpqPgaS/pkg6H8Hp8pbtQ6kxCu/Zv+YtT60X7uryz5fhdMqZrpqTw7QYY=; ftkrc_=808de12e-71c4-448a-98b5-5088f7029765; select_city=110000; lianjia_token=2.0014087c5d42e6d8bf05a5556c1d4b0648; lianjia_token_secure=2.0014087c5d42e6d8bf05a5556c1d4b0648'}

start_time = time.time()

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
        for index_main_page in range(1, 100):
            try:
                resp1 = requests.get(f"https://bj.lianjia.com/chengjiao/{District}/pg{index_main_page}/",headers=headers)
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
                    resp2 = requests.get(href, headers=headers)
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

                    file_path = '/Users/jia/Desktop/学习 /科研/独立论文部分/北京二手房数据(链家)_test.xlsx'

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