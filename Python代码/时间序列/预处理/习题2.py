import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from statsmodels.graphics.tsaplots import plot_acf
from matplotlib.dates import DateFormatter

plt.rcParams['font.sans-serif'] = ['Arial Unicode MS']

# 读取数据
data = pd.read_excel('/Users/jia/Desktop/学习/Python代码/数据挖掘/习题数据（EXCEL格式）/E2_2.xlsx')

# 绘制时间序列图
plt.figure(figsize=(10, 5))
plt.plot(data['time'], data['co2'], 'o-')
plt.title('CO2浓度时间序列图')
plt.xlabel('时间')
plt.ylabel('CO2浓度')
plt.show()


# 绘制自相关图
plt.figure(figsize=(10, 5))
plot_acf(data['co2'], lags=24)
plt.title('自相关函数')
plt.xlabel('延迟k阶')
plt.ylabel('自相关系数')
plt.show()

# 自相关系数
from statsmodels.tsa.stattools import acf
acf_values, confint = acf(data['co2'], nlags=24, fft=False, alpha=0.05)
print("自相关系数（前24阶）:", acf_values[:25])  # 注意索引从0开始，所以取到24
