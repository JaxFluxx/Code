import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from statsmodels.graphics.tsaplots import plot_acf
from matplotlib.dates import DateFormatter

plt.rcParams['font.sans-serif'] = ['Arial Unicode MS']


data = pd.read_excel('/Users/jia/Desktop/学习/Python代码/数据挖掘/习题数据（EXCEL格式）/E2_5.xlsx')
# print(data.head())

# 绘制时序图
plt.figure(figsize=(12, 6))
plt.plot(data['time'],data['x'], 'r--')
plt.xlabel('时间')
plt.ylabel('销售额')
plt.title('时间序列图')
plt.show()

# 绘制自相关图
plt.figure(figsize=(12, 6))
plot_acf(data['x'],lags = 12)
plt.xlabel('滞后阶数')
plt.ylabel('自相关系数')
plt.title('自相关图')
plt.show()


# 纯随机性检验
plot_acf(data['x']).show()