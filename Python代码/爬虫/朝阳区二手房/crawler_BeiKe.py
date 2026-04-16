# 从主界面获取子界面的链接
# 爬取子界面的数据：价格，面积，单价，楼层，区域+小区名字，建成年代，经纬度
# 保存到xlsx文件中

# 从xlsx文件中用pandas读取数据，数据清洗
# 数据可视化

import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import os
import random
import re


headers = {
    "User-Agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0"
}

start_time = time.time()

try:
    for index_main_page in range(1, 81):
        resp1 = requests.get(f"https://bj.ke.com/ershoufang/chaoyang/pg{index_main_page}/", headers=headers)
        resp1.raise_for_status()
        # print("主界面链接获取成功")
        resp1.encoding = "utf-8"

        main_page = BeautifulSoup(resp1.text, "html.parser")
        print(f"主界面第{index_main_page}页解析成功...")
        # print(main_page)

        # 获取此页所有子页面链接
        child_list = main_page.find("ul", class_='sellListContent').find_all('a', class_="VIEWDATA CLICKDATA maidian-detail")
        #print(child_list)

        resp1.close()
##########################################################################
        index_child_page = 0
        for child in child_list:    # 每一个子页面链接
            index_child_page += 1
            print(f"正在爬取第{index_main_page}页第{index_child_page}个子页面..." , end = '')

            href = child.get('href')
            #print(f"链接：{href}")

            # 获取子界面数据
            resp2 = requests.get(href, headers=headers)
            resp2.raise_for_status()
            # print("子界面数据获取成功")
            resp2.encoding = "utf-8"

            child_page = BeautifulSoup(resp2.text, "html.parser")
            # print(child_page)



            # 价格
            price = child_page.find("span", class_="total").text.strip()
            # print(f"价格：{price}万元")

            # 户型
            house_type = child_page.find("div", class_="mainInfo").text.strip()

            # 面积
            area_text = child_page.find('div', class_="area").text.strip()
            area = re.findall(r'\d+', area_text)[0]  # 提取数字部分
            # print(f"面积：{area}")

            # 单价
            unit_price = child_page.find('span', class_="unitPriceValue").text.strip()
            # print(f"单价：{unit_price}元/平米")

            # 年份
            # 找到包含建成年代信息的<span>标签
            year = child_page.find_all("span", class_="xiaoqu_main_info")[1].text.strip()
            #print(f"建成年代：{year}")


            # 区域
            region = child_page.find("div", class_="areaName").find("span", class_="info").text.strip().replace(" ", "").replace("\n", "")
            # print(f"区域：{region}")

            # 小区
            community = child_page.find("div", class_="communityName").find("a").text.strip()
            # print(f"小区：{community}")

            # 贝壳编号
            num_text = child_page.find("div", class_="houseRecord").find("span", class_="info").text.strip()
            num = re.match(r'\d+', num_text).group()
            print(f"贝壳编号：{num}")


            # 经纬度（动态网页，正则表达式）
            location_pattern = re.compile(r"resblockPosition:\s*'(-?\d+\.\d+),\s*(-?\d+\.\d+)'", re.S)

            # 使用search方法查找匹配项
            match = location_pattern.search(resp2.text)

            if match:
                longitude = match.group(1)
                latitude = match.group(2)
                print(f"经纬度：{longitude}, {latitude}")
            else:
                print("未找到匹配的经纬度信息")

            resp2.close()

            # 保存到xlsx文件中
            data = {
                '贝壳编号': [num],
                '经度': [longitude],
                '纬度': [latitude],
                '价格(万元)': [price],
                '面积(平米)': [area],
                '户型': [house_type],
                '单价(元/平米)': [unit_price],
                '区域': [region],
                '小区': [community],
                '建成年代': [year]
            }

            dataframe_name = pd.DataFrame(data)

            file_path = r'C:\Users\何嘉\Desktop\朝阳二手房数据经纬度_贝壳网test.xlsx'

            if os.path.exists(file_path):
                existing_data = pd.read_excel(file_path)
                dataframe_name = pd.concat([existing_data, dataframe_name], ignore_index=True)

            dataframe_name.to_excel(file_path, index=False)

            print('成功下载！----', end='')
            end_time = time.time()
            print(
                f"用时：{round((end_time - start_time) // 60)}分{round((end_time - start_time) % 60)}秒")

            time.sleep(random.randint(1, 2))
        time.sleep(5)
    time.sleep(30)

except requests.exceptions.RequestException as e:
    print(f"{e}获取链接失败")
