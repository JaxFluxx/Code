import pandas as pd
import numpy as np
import random
import matplotlib.pyplot as plt
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error
from statsmodels.tsa.arima.model import ARIMA

plt.rcParams['font.sans-serif'] = ['Arial Unicode MS']  # 支持中文

# ---------- 基本设置 ---------- #
mean_price = 549.6649639920413
std_price = 343.7072939272807

train_path = '/Users/jia/Desktop/论文/数据/数据处理/北京二手房成交_1.9_train.csv'
test_path = '/Users/jia/Desktop/论文/数据/数据处理/北京二手房成交_1.9_test.csv'

print("📥 正在读取训练和测试数据...")
train_df = pd.read_csv(train_path)
test_df = pd.read_csv(test_path)

# 移除 id 列
train_df = train_df.drop('id', axis=1)
test_df = test_df.drop('id', axis=1)

# ---------- 特征/标签准备 ---------- #
print("📊 正在分离特征和目标变量...")
X_train = train_df.iloc[:, :-1]
y_train = train_df.iloc[:, -1]
X_test = test_df.iloc[:, :-1]
y_test = test_df.iloc[:, -1]

# ---------- 类型转换 ---------- #
print("🔄 正在处理类别型特征...")
for col in X_train.columns:
    if X_train[col].dtype == 'object':
        X_train[col] = X_train[col].astype('category')
        X_test[col] = X_test[col].astype('category')

# ---------- ARIMA 模型训练 ---------- #
print("🚀 正在训练 ARIMA 模型...")
# ARIMA 模型一般用于时间序列数据，所以假设 y_train 是时间序列
model = ARIMA(y_train, order=(5, 1, 0))  # (p, d, q) 参数可以根据数据调整
model_fit = model.fit()

# ---------- 模型预测 ---------- #
print("🔍 正在进行预测...")
y_pred = model_fit.forecast(steps=len(y_test))

# ---------- 反归一化 ---------- #
y_pred_original = y_pred * std_price + mean_price
y_test_original = y_test * std_price + mean_price

# ---------- 评估指标 ---------- #
print("\n📈 模型评估结果：")
r2 = r2_score(y_test_original, y_pred_original)
mae = mean_absolute_error(y_test_original, y_pred_original)
rmse = mean_squared_error(y_test_original, y_pred_original, squared=False)
print(f"R² Score: {r2:.4f}")
print(f"MAE（平均绝对误差）: {mae:.2f}")
print(f"RMSE（均方根误差）: {rmse:.2f}")

# ---------- 误差分析（百分比） ---------- #
print("\n📊 正在计算预测误差百分比...")
percent_errors = []
for i in range(len(y_test_original)):
    true_price = y_test_original.iloc[i]  # 使用 .iloc 来确保按位置访问
    pred_price = y_pred_original[i]  # 对预测价格同样使用索引
    percent_error = abs(pred_price - true_price) / true_price * 100 if true_price != 0 else float('nan')
    percent_errors.append(percent_error)

# 平均误差百分比
average_percent_error = np.nanmean(percent_errors)
print(f"\n📉 平均预测误差百分比: {average_percent_error:.2f}%")

# 随机打印 100 条预测误差
print("\n🔢 随机抽取 100 条预测误差（相对真实房价百分比）：")
sample_indices = random.sample(range(len(percent_errors)), min(100, len(percent_errors)))
for i in sample_indices:
    print(f"样本 {i + 1}: 真实={y_test_original.iloc[i]:.2f}, 预测={y_pred_original[i]:.2f}, 误差={percent_errors[i]:.2f}%")


# ---------- 可视化 ---------- #
print("\n📊 正在绘制预测结果对比图（采样 100 个样本）...")
sample_size = 100
sorted_index = np.argsort(y_test_original)
step = len(y_test_original) // sample_size
sample_indices = sorted_index[::step][:sample_size]

sample_true = y_test_original[sample_indices]
sample_pred = y_pred_original[sample_indices]

plt.figure(figsize=(12, 6))
plt.plot(range(sample_size), sample_true, label='Actual Price', color='green', linewidth=2)
plt.plot(range(sample_size), sample_pred, label='Predicted Price', color='blue', linestyle='--', linewidth=2)
plt.title('Line Plot: Predicted vs Actual Housing Prices (Sampled)', fontsize=16)
plt.xlabel('Sample Index (Sampled)', fontsize=12)
plt.ylabel('Price', fontsize=12)
plt.legend()
plt.grid(True)
plt.tight_layout()

plt.show()
