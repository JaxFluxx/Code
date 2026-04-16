#1.获取子页面链接
#2.获取图片src链接
#3.下载图片

import requests
from bs4 import BeautifulSoup
import os
import time

start_time = time.time()

headers = {
    "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0"
}
try:

    save_path = "D:/python_file/优美爬虫/"  # 设置保存路径
    os.makedirs(save_path, exist_ok=True)  # 创建文件夹
    # file_name = "优美爬虫"   # 设置文件名
    # save_path = os.path.join(save_path, file_name)   # 拼接路径

    for index in range(20,73):
        #主链接
        resp = requests.get(f"https://www.umeituku.com/bizhitupian/meinvbizhi/{index}.htm", headers=headers)
        resp.raise_for_status()
        print(f"第{index}页获取链接成功...")
        resp.encoding = "utf-8"   #设置编码
        #print(resp.text)

        main_page = BeautifulSoup(resp.text, "html.parser")   #解析网页
        #print("解析网页成功...")

        #这里的class后面一定要加个_
        alist = main_page.find("div", class_ = "TypeList").find_all("a")   #获取子页面链接列表
        #print(alist)

        #标记是第几张图片
        num = 0;
        for a in alist:
            num += 1;
            #子链接
            href = a.get("href")   #获取子页面链接

            resp2 = requests.get(href)
            resp2.raise_for_status()
            resp2.encoding = "utf-8"   #设置编码

            main_page2 = BeautifulSoup(resp2.text, "html.parser")   #解析子页面
            #print("解析子页面成功...")

            blist = main_page2.find_all("p", align = "center")   #获取图片src链接列表
            #print(blist)

            for img in blist:
                src = img.find("img").get("src")   #获取图片src链接
                #print(f"第{index}页第{num}张照片下载地址获取成功...")
                #print(src)

                #下载图片
                resp3 = requests.get(src)   #获取图片jpg文件
                zijie = resp3.content   #获取图片二进制数据
                #网址后部分为名字
                name = src.split("/")[-1]   #获取图片名字

                save_path = "D:/python_file/优美爬虫/"   # 刷新前半段保存路径
                save_path = os.path.join(save_path, name)  # 拼接路径
                with open(save_path, mode="wb") as f:
                    f.write(zijie)   #写入图片数据


                print(f"第{index}页第{num}张照片下载成功...")

                time.sleep(1)

    each_time = time.time()
    gap = each_time - start_time
    print(f"到第{gap}页总耗时：", )
    resp.close()
    resp2.close()
    resp3.close()
except requests.exceptions.RequestException as e:
    print(f"{e}获取链接失败")

end_time = time.time()
print("总共耗时：", end_time - start_time)