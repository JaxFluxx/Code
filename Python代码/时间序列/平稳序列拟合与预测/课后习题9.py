import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from statsmodels.tsa.stattools import adfuller, acf, pacf
from statsmodels.tsa.arima.model import ARIMA

# 读取数据
file_path = '/Users/jia/Desktop/学习 /Python代码/时间序列/平稳序列拟合与预测/E4_9.xlsx'
df = pd.read_excel(file_path)

# 转换日期格式
df['t'] = pd.to_datetime(df['t'], format='%b-%y')
df.set_index('t', inplace=True)

# 检验平稳性（ADF检验）
adf_result = adfuller(df['x'])
print('ADF Statistic:', adf_result[0])
print('p-value:', adf_result[1])

# 纯随机性检验（自相关函数）
plt.figure(figsize=(12, 6))
plt.subplot(121)
plt.plot(acf(df['x'], nlags=20))
plt.title('Autocorrelation Function')

plt.subplot(122)
plt.plot(pacf(df['x'], nlags=20))
plt.title('Partial Autocorrelation Function')
plt.show()

# 建立ARIMA模型，拟合序列
model = ARIMA(df['x'], order=(1, 1, 1))
model_fit = model.fit()
print(model_fit.summary())

# 绘制拟合与预测
df['forecast'] = model_fit.predict(start=0, end=len(df)-1, dynamic=False)

# 预测未来5年（20个季度）
forecast = model_fit.forecast(steps=20)
forecast_index = pd.date_range(df.index[-1] + pd.DateOffset(months=3), periods=20, freq='Q')
forecast_series = pd.Series(forecast, index=forecast_index)

# 绘图
plt.figure(figsize=(12, 6))
plt.plot(df['x'], label='Original Series')
plt.plot(df['forecast'], label='Fitted Series', linestyle='--')
plt.plot(forecast_series, label='Forecast for Next 5 Years', linestyle='--')
plt.legend()
plt.title('Time Series, Fitted Series, and Forecast')
plt.show()
