import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf

plt.rcParams['font.sans-serif'] = ['Arial Unicode MS']

# 生成一个等差数列
# arr = np.arange(start, stop, step)
data = np.arange(1, 21)

# 绘制自相关图
plt.plot(15,6)
plot_acf(data, lags=6)
plt.title('自相关函数')
plt.xlabel('延迟k阶')
plt.ylabel('自相关系数')
plt.show()

# 输出前6阶样本自相关系数的值
from statsmodels.tsa.stattools import acf
acf_values, confint, qstat, pvalues = acf(data['co2'], nlags=24, fft=False, alpha=0.05)
print("自相关系数（前24阶）:", acf_values[:25])  # 注意索引从0开始，所以取到24