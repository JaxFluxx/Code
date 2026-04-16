from bs4 import BeautifulSoup
import pandas as pd
import requests
import json
import time
import os

def fetchUrl(url):
    header = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36',
    }

    r = requests.get(url, headers=header)
    r.encoding = "utf-8"
    return r

def parseJson(jsonStr):

    jsonObj = json.loads(jsonStr)
    data = jsonObj['data']

    for item in data:
        name = item["author"]["name"]
        print("正在爬取", name, "的回答")
        headline = item["author"]["headline"]
        dateTIme = time.strftime("%Y-%m-%d", time.localtime(item['updated_time']))
        comment_count = item['comment_count']
        voteup_count = item['voteup_count']
        content = parseHtml(item["content"])

        # print(name, headline, dateTIme, comment_count, voteup_count, content)

        yield [[name, headline, dateTIme, comment_count, voteup_count, content]]

def parseHtml(html):

    bsObj = BeautifulSoup(html, "lxml")
    images = bsObj.find_all("noscript")

    if(len(images) == 0):
        print("回答内容无图片")
    else:
        print("回答中共有",len(images),"张图片，正在下载……")
        for item in images:
            link = item.img['data-original']
            downloadImage(link, "D:/python_file/")
        print("图片下载完成")

    return bsObj.text

def downloadImage(url, path):

    bytes = fetchUrl(url).content
    # url : https://pic3.zhimg.com/c7ad985268e7144b588d7bf94eedb487_r.jpg?source=1940ef5c
    # filename: c7ad985268e7144b588d7bf94eedb487_r.jpg
    filename = url.split("?")[0].split("/")[-1]

    # 如果没有该文件夹，则自动生成
    if not os.path.exists(path):
        os.makedirs(path)

    with open(path + filename, "wb+") as f:
        f.write(bytes)

def saveData(data, filename):

    dataframe = pd.DataFrame(data)
    dataframe.to_csv(filename, mode='a', index=False, sep=',', header=False, encoding="utf_8_sig")

if __name__ == "__main__":

    # 保存的文件名
    filename = "data.csv"
    qid = 583793972
    offset = 0
    totalNum = 50

    while offset < totalNum:
        url = "https://www.zhihu.com/api/v4/questions/{0}/answers?include=data%5B%2A%5D.is_normal%2Cadmin_closed_comment%2Creward_info%2Cis_collapsed%2Cannotation_action%2Cannotation_detail%2Ccollapse_reason%2Cis_sticky%2Ccollapsed_by%2Csuggest_edit%2Ccomment_count%2Ccan_comment%2Ccontent%2Ceditable_content%2Cvoteup_count%2Creshipment_settings%2Ccomment_permission%2Ccreated_time%2Cupdated_time%2Creview_info%2Crelevant_info%2Cquestion%2Cexcerpt%2Crelationship.is_authorized%2Cis_author%2Cvoting%2Cis_thanked%2Cis_nothelp%2Cis_labeled%2Cis_recognized%2Cpaid_info%2Cpaid_info_content%3Bdata%5B%2A%5D.mark_infos%5B%2A%5D.url%3Bdata%5B%2A%5D.author.follower_count%2Cbadge%5B%2A%5D.topics&limit=5&offset={1}&platform=desktop&sort_by=default" .format(qid, offset)
        html = fetchUrl(url).text

        for data in parseJson(html):
            # print(data)
            saveData(data, filename)

            offset += 1
            print("已经爬取完成",offset,"条回答数据，一共有",totalNum, "条")
            print("---"*20)

