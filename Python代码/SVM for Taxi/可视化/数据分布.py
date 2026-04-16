import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# 设置苹果系统中文字体
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题

file_path = r'/Users/jia/Desktop/学习 /机器学习/数据/1.3.csv'
df = pd.read_csv(file_path)

# 计算合理的区间数函数（斯特吉斯公式）
def calc_bins(series):
    n = series.dropna().shape[0]
    bins = int(np.ceil(np.log2(n)) + 1)
    return bins

# 画 Trip Miles 折线图
plt.figure(figsize=(10, 5))
bins_miles = calc_bins(df['Trip Miles'])
# 分箱
counts_miles, bin_edges_miles = np.histogram(df['Trip Miles'].dropna(), bins=bins_miles, range=(0, 200))
# 计算每个区间的中点
bin_centers_miles = (bin_edges_miles[:-1] + bin_edges_miles[1:]) / 2

plt.plot(bin_centers_miles, counts_miles, marker='o', linestyle='-', color='skyblue')
plt.title('出租车行程距离（Trip Miles）分布折线图')
plt.xlabel('行程距离（英里）')
plt.ylabel('频数')
plt.xlim(0, 40)
plt.ylim(0, None)
plt.grid(True)
plt.show()


# 画 Trip Seconds 折线图
plt.figure(figsize=(10, 5))
bins_seconds = calc_bins(df['Trip Seconds'])
counts_seconds, bin_edges_seconds = np.histogram(df['Trip Seconds'].dropna(), bins=bins_seconds, range=(0, 5000))
bin_centers_seconds = (bin_edges_seconds[:-1] + bin_edges_seconds[1:]) / 2

plt.plot(bin_centers_seconds, counts_seconds, marker='o', linestyle='-', color='orange')
plt.title('出租车行程时长（Trip Seconds）分布折线图')
plt.xlabel('行程时长（秒）')
plt.ylabel('频数')
plt.xlim(0, 5000)
plt.ylim(0, None)
plt.grid(True)
plt.show()
