
# 数据读取：代码从文件 E4_1.xlsx 中读取数据，并将 x 列提取为利润序列。
# 时序图绘制：绘制利润的时间序列图，显示利润随时间的波动。
# 平稳性检验：使用ADF检验来判断时间序列是否平稳，并打印出统计值和p值。
# 自相关性分析：绘制自相关函数（ACF）和偏自相关函数（PACF）以分析数据的自相关性。
# 模型拟合：选择ARIMA(1, 1, 1)模型来拟合数据。
# 未来预测：利用ARIMA模型预测未来60个月的利润，并绘制预测图，带有置信区间。


# 导入必要的库
import pandas as pd
import matplotlib.pyplot as plt
import statsmodels.api as sm
from statsmodels.tsa.stattools import adfuller, acf, pacf
from statsmodels.tsa.arima.model import ARIMA

plt.rcParams['font.sans-serif'] = ['Arial Unicode MS'] #苹果系统显示中文字体

# 1. 读取数据
data = pd.read_excel('E4_1.xlsx')
profits = data['x']

# 2. 绘制时序图
plt.figure(figsize=(10, 5))
plt.plot(data['t'], profits, marker='o')
plt.title("月利润时间序列图")
plt.xlabel("时间（月）")
plt.ylabel("利润（万元）")
plt.grid(True)
plt.show()

# 3. 判断序列的平稳性
adf_test = adfuller(profits)
print("ADF 统计量:", adf_test[0])
print("p值:", adf_test[1])
for key, value in adf_test[4].items():
    print(f'临界值 ({key}): {value}')

# 4. 自相关性和偏自相关性分析
plt.figure(figsize=(12, 6))

plt.subplot(121)
sm.graphics.tsa.plot_acf(profits, lags=20, ax=plt.gca())
plt.title("自相关函数")

plt.subplot(122)
sm.graphics.tsa.plot_pacf(profits, lags=20, ax=plt.gca())
plt.title("偏自相关函数")

plt.tight_layout()
plt.show()

# 5. 模型拟合
model = ARIMA(profits, order=(1, 1, 1))
model_fit = model.fit()

print(model_fit.summary())

# 6. 利用模型进行未来预测
forecast = model_fit.get_forecast(steps=60)
forecast_index = range(len(profits) + 1, len(profits) + 61)
forecast_values = forecast.predicted_mean
conf_int = forecast.conf_int()

plt.figure(figsize=(10, 5))
plt.plot(data['t'], profits, label="实际数据", marker='o')
plt.plot(forecast_index, forecast_values, color='red', label="预测数据")
plt.fill_between(forecast_index, conf_int.iloc[:, 0], conf_int.iloc[:, 1], color='pink', alpha=0.3)
plt.title("未来5年利润预测")
plt.xlabel("时间（月）")
plt.ylabel("利润（万元）")
plt.legend()
plt.grid(True)
plt.show()

