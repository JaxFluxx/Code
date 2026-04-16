import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.svm import SVR
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error
from tqdm import tqdm
import random

plt.rcParams['font.sans-serif'] = ['Arial Unicode MS']  # macOS 显示中文字体

# ---------- 进度条设置 ----------
steps_total = 7
progress = tqdm(total=steps_total, desc='程序总进度', ncols=100)

# ---------- 参数 ----------
mean_price = 549.6649639920413
std_price = 343.7072939272807
train_path = '/Users/jia/Desktop/论文/数据/数据处理/北京二手房成交_1.9_train.csv'
test_path = '/Users/jia/Desktop/论文/数据/数据处理/北京二手房成交_1.9_test.csv'

# ---------- Step 1: 读取数据 ----------
train_df = pd.read_csv(train_path)
test_df = pd.read_csv(test_path)
progress.update(1)

# ---------- Step 2: 分离特征与标签 ----------
X_train = train_df.iloc[:, :-1]
y_train = train_df.iloc[:, -1]
X_test = test_df.iloc[:, :-1]
y_test = test_df.iloc[:, -1]
progress.update(1)

# ---------- Step 3: 类别编码 ----------
for col in X_train.columns:
    if X_train[col].dtype == 'object':
        X_train[col] = X_train[col].astype('category').cat.codes
        X_test[col] = X_test[col].astype('category').cat.codes
progress.update(1)

# ---------- Step 4: 创建 SVR 模型 ----------
svr_model = SVR(kernel='rbf', C=100, epsilon=0.1)
svr_model.fit(X_train, y_train)
progress.update(1)

# ---------- Step 5: 预测与还原 ----------
y_pred = svr_model.predict(X_test)
y_pred_original = y_pred * std_price + mean_price
y_test_original = y_test * std_price + mean_price
progress.update(1)

# ---------- Step 6: 模型评估 ----------
r2 = r2_score(y_test_original, y_pred_original)
mae = mean_absolute_error(y_test_original, y_pred_original)
rmse = mean_squared_error(y_test_original, y_pred_original, squared=False)

print("\n模型评估（SVR）：")
print(f"R² Score: {r2:.4f}")
print(f"MAE（平均绝对误差）: {mae:.2f}")
print(f"RMSE（均方根误差）: {rmse:.2f}")
progress.update(1)

# ---------- Step 7: 随机打印 100 个误差 ----------
print("\n预测误差（相对真实房价百分比，随机抽样 100 个）：")
n = len(y_test_original)
indices = random.sample(range(n), min(100, n))

errors = []
for i in indices:
    true_price = y_test_original[i]
    pred_price = y_pred_original[i]
    percent_error = abs(pred_price - true_price) / true_price * 100 if true_price != 0 else float('nan')
    errors.append(percent_error)
    print(f"样本 {i + 1}: 真实={true_price:.2f}, 预测={pred_price:.2f}, 误差={percent_error:.2f}%")

# ---------- 平均误差百分比 ----------
avg_percent_error = np.nanmean(errors)
print(f"\n平均误差百分比: {avg_percent_error:.2f}%")
progress.update(1)

# ---------- 可视化：预测 vs 真实 ----------
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

# ---------- 关闭进度条 ----------
progress.close()
