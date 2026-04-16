import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats

# 设置Matplotlib使用中文字体
plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号

# 读取Excel文件
file_path = r"C:\Users\何嘉\Desktop\朝阳二手房贝壳\朝阳二手房数据_贝壳网_清洗后.test.xlsx"
df = pd.read_excel(file_path)

# 确保数据正确读取
print(df.head())

# 数据清洗：去除可能的空值
df.dropna(inplace=True)

# 基础统计分析
print("\n基础统计信息：")
print(df.describe())

# 筛选出房价在200万到400万之间的房子
filtered_df = df.query('800 <= `价格(万元)`')

# 将筛选后的数据保存到新的Excel文件中
filtered_df.to_excel(r"C:\Users\何嘉\Desktop\朝阳二手房贝壳\朝阳二手房数据_贝壳网_清洗后_morethan800.xlsx", index=False)
