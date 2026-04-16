#!/usr/bin/python3
from bs4 import BeautifulSoup
import requests
import os

# 设置请求头
headers = {
    "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0"
}

try:
    #设置好保存路径和文件名字
    save_path = "D:/python_file/"
    os.makedirs(save_path, exist_ok=True)
    file_name = "豆瓣电影top250.txt"
    save_file = os.path.join(save_path, file_name)


    for num in range(0, 250, 25):
        # 发送请求,content是响应对象
        print("正在获取网页...")
        content = requests.get(f"https://movie.douban.com/top250?start={num}", headers=headers)
        content.raise_for_status()  # 检查响应状态码是否为200，否则抛出异常
        print("网页获取成功！")
        soup = BeautifulSoup(content.text, "html.parser")   #html.parser是解析器,解析content.text,返回soup对象
        all_titles = soup.find_all("span", attrs={"class":"title"})  # 找到所有h3标签
        print(all_titles)

        with open(save_file, "a", encoding="utf-8") as file:
            for title in all_titles:
                if "/" not in title.text:  # 排除非电影标题
                    print(title.string)
                    file.write(title.string + "\n")
        print(f"保存成功！文件路径：{save_file}")


except requests.exceptions.RequestException as e:
    print(f"Error: {e}")


