import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.statespace.sarimax import SARIMAX

# Step 1: 输入数据
years = list(range(1949, 2009))
pop_data = [
    54167, 55196, 56300, 57482, 58796, 60266, 61465, 62828, 64653, 65994,
    67207, 66207, 65859, 67295, 69172, 70499, 72538, 74542, 76368, 78534,
    80671, 82992, 85229, 87177, 89211, 90859, 92420, 93717, 94974, 96259,
    97542, 98705, 100072, 101654, 103008, 104357, 105851, 107507, 109300, 111026,
    112704, 114333, 115823, 117171, 118517, 119850, 121121, 122389, 123626, 124761,
    125786, 126743, 127627, 128453, 129227, 129988, 130756, 131448, 132129, 132802
]

# 数据整理成 DataFrame
pop_df = pd.DataFrame({'Year': years, 'Population': pop_data})
pop_df.set_index('Year', inplace=True)

# Step 2: 数据平稳化处理（用于 ARMA）
pop_diff = pop_df.diff().dropna()

# Step 3: 拟合 ARMA 模型（p=2, q=2）
arma_model = ARIMA(pop_diff, order=(2, 0, 2)).fit()
arma_fitted = arma_model.fittedvalues.cumsum() + pop_df.iloc[0, 0]  # 还原拟合值
arma_forecast_diff = arma_model.forecast(steps=8)  # 差分预测
arma_forecast = arma_forecast_diff.cumsum() + pop_df.iloc[-1, 0]  # 还原预测值

# Step 4: 拟合 ARIMA 模型（p=2, d=1, q=2）
arima_model = ARIMA(pop_df, order=(2, 1, 2)).fit()
arima_fitted = arima_model.fittedvalues
arima_forecast = arima_model.forecast(steps=8)

# Step 5: 拟合 SARIMA 模型（p=2, d=1, q=2，季节性参数 (1, 1, 1, 12)）
sarima_model = SARIMAX(pop_df, order=(2, 1, 2), seasonal_order=(1, 1, 1, 12)).fit()
sarima_fitted = sarima_model.fittedvalues
sarima_forecast = sarima_model.forecast(steps=8)

# Step 6: 绘制拟合图（1949-2008 年）
plt.figure(figsize=(10, 6))
plt.plot(pop_df, label='Original Data', color='black')
plt.plot(pop_df.index[1:], arma_fitted, label='ARMA Fitted', linestyle='--', color='blue')
plt.plot(pop_df.index, arima_fitted, label='ARIMA Fitted', linestyle='-.', color='green')
plt.plot(pop_df.index, sarima_fitted, label='SARIMA Fitted', linestyle=':', color='red')
plt.title('Model Fitting (1949-2008)')
plt.xlabel('Year')
plt.ylabel('Population (10,000)')
plt.legend()
plt.grid()
plt.show()

# Step 7: 绘制预测图（2009-2016 年）
future_years = list(range(2009, 2017))
plt.figure(figsize=(10, 6))
plt.plot(future_years, arma_forecast, label='ARMA Forecast', linestyle='--', color='blue')
plt.plot(future_years, arima_forecast, label='ARIMA Forecast', linestyle='-.', color='green')
plt.plot(future_years, sarima_forecast, label='SARIMA Forecast', linestyle=':', color='red')
plt.title('Population Forecast (2009-2016)')
plt.xlabel('Year')
plt.ylabel('Population (10,000)')
plt.legend()
plt.grid()
plt.show()

# Step 8: 输出预测结果
print("ARMA 预测结果 (2009-2016):")
print(arma_forecast)

print("\nARIMA 预测结果 (2009-2016):")
print(arima_forecast)

print("\nSARIMA 预测结果 (2009-2016):")
print(sarima_forecast)