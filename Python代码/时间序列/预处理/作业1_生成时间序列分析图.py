import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

plt.rcParams['font.sans-serif'] = ['Arial Unicode MS']

# 读取数据
data = pd.read_excel('/Users/jia/Desktop/学习/时间序列/时间序列分析——基于python案例数据/A1_3.xlsx')
print(data)

# 假设数据集中有一个日期列名为 'year' 和一个数值列名为 'sunspot'
# 将日期列转换为日期时间格式
data['year'] = pd.to_datetime(data['year'])  # 转换为年份格式

# 设置索引为日期列
data.set_index('year', inplace=True)  # set_index()方法设置索引列

# 绘制时序图
plt.figure(figsize=(12, 6))
plt.plot(data.index, data['sunspot'], label='时间序列', color='blue')  # 参数1：索引，参数2：数值列名

plt.title('时序图示例')
plt.xlabel('年份')
plt.ylabel('太阳黑子数量')
plt.legend()
plt.grid()
plt.show()
