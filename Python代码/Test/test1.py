import matplotlib.pyplot as plt
import pandas as pd

# 数据
data = [-2.000, -0.703, -2.232, -2.535, -1.662, -0.152, 2.155, 2.298, 0.886, 1.871, 1.933,
        2.221, 0.328, -0.103, 0.337, 1.334, 0.864, 0.205, 0.555, 0.883, 1.734, 0.824,
        -1.054, 1.015, 1.479, 1.158, 1.002, -0.415, -0.193, -0.502, -0.316, -0.421, -0.448,
        -2.115, 0.271, -0.558, -0.045, -0.221, -0.875, -0.014, 1.746, 1.481, 0.950, 1.714,
        0.220, -1.924, -1.217, -1.907, 0.200, -0.237]

# 创建时间序列
time_series = pd.Series(data)

# 绘制时序图
plt.figure(figsize=(10, 6))
time_series.plot()
plt.title('Time Series Plot')
plt.xlabel('Month')
plt.ylabel('Profit/Loss (in ten thousand yuan)')
plt.grid(True)
plt.show()

from statsmodels.tsa.stattools import adfuller, acf, pacf
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf

# 平稳性检验（ADF检验）
result = adfuller(time_series)
print('ADF Statistic:', result[0])
print('p-value:', result[1])
for key, value in result[4].items():
    print('Critical Value (%s) = %.3f' % (key, value))

# 纯随机性检验（Ljung-Box检验）
ljung_box_result = pd.Series(acf(time_series, nlags=20))[1:].dropna().rolling(window=20).apply(lambda x: (x**2).sum())
print(ljung_box_result)

# 自相关图和偏自相关图
plot_acf(time_series)
plot_pacf(time_series)
plt.show()

# 自相关图和偏自相关图
plot_acf(time_series)
plot_pacf(time_series)
plt.show()
from statsmodels.tsa.arima.model import ARIMA

# 拟合ARIMA模型
model = ARIMA(time_series, order=(1, 1, 1))
model_fit = model.fit()
print(model_fit.summary())
# 预测未来60个月
forecast = model_fit.forecast(steps=60)
print(forecast)