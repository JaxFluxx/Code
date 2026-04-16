import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import time
from tqdm import tqdm
from xgboost import XGBRegressor
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error
from sklearn.model_selection import ParameterGrid

plt.rcParams['font.sans-serif'] = ['Arial Unicode MS']  # mac 中文字体支持

# -------- 开始计时 -------- #
start_time = time.time()

# -------- 数据参数 -------- #
mean_price = 549.6649639920413
std_price = 343.7072939272807

train_path = '/Users/jia/Desktop/论文/数据/数据处理/北京二手房成交_1.9_train.csv'
test_path = '/Users/jia/Desktop/论文/数据/数据处理/北京二手房成交_1.9_test.csv'

print("📥 正在读取数据...")
train_df = pd.read_csv(train_path)
test_df = pd.read_csv(test_path)

# 移除 id 列
train_df = train_df.drop('id', axis=1)
test_df = test_df.drop('id', axis=1)

X_train = train_df.iloc[:, :-1]
y_train = train_df.iloc[:, -1]
X_test = test_df.iloc[:, :-1]
y_test = test_df.iloc[:, -1]

# -------- 编码非数值特征 -------- #
print("🔢 正在转换类别变量为数值...")
for col in X_train.columns:
    if X_train[col].dtype == 'object':
        X_train[col] = X_train[col].astype('category').cat.codes
        X_test[col] = X_test[col].astype('category').cat.codes

# -------- 参数网格 -------- #
param_grid = {
    'n_estimators': [350,400, 500, 600],
    'max_depth': [8, 9, 10, 11],
    'learning_rate': [0.15,0.2, 0.25, 0.3],
    'subsample': [0.8, 0.9, 1],
    'colsample_bytree': [0.8, 0.9, 1]
}


print("🔍 正在使用自定义 GridSearchCV + tqdm 进行调参（XGBoost）...")
param_list = list(ParameterGrid(param_grid))
progress_bar = tqdm(total=len(param_list), desc="⏳ GridSearchCV Progress", ncols=80)

best_score = float('inf')
best_params = None
best_model = None

last_log_time = time.time()

for params in param_list:
    model = XGBRegressor(objective='reg:squarederror', random_state=42, n_jobs=-1, **params)
    model.fit(X_train, y_train)

    preds = model.predict(X_train)
    score = mean_squared_error(y_train, preds)

    if score < best_score:
        best_score = score
        best_params = params
        best_model = model

    progress_bar.update(1)

    if time.time() - last_log_time > 10:
        elapsed = time.time() - start_time
        progress = progress_bar.n / progress_bar.total
        estimated_total = elapsed / progress if progress > 0 else 0
        remaining = estimated_total - elapsed
        print(f"⏱️ 已完成 {progress_bar.n}/{progress_bar.total}，剩余估计时间：{remaining:.1f} 秒")

        last_log_time = time.time()

progress_bar.close()

print("\n✅ 最佳参数组合为:")
print(best_params)

# -------- 模型预测 -------- #
print("📈 正在进行预测...")
y_pred = best_model.predict(X_test)

# -------- 还原价格 -------- #
y_pred_original = y_pred * std_price + mean_price
y_test_original = y_test * std_price + mean_price

# -------- 评估指标 -------- #
r2 = r2_score(y_test_original, y_pred_original)
mae = mean_absolute_error(y_test_original, y_pred_original)
rmse = mean_squared_error(y_test_original, y_pred_original, squared=False)

print("\n📊 模型评估（XGBoost）：")
print(f"R² Score: {r2:.4f}")
print(f"MAE: {mae:.2f}")
print(f"RMSE: {rmse:.2f}")

# -------- 平均百分比误差 -------- #
percent_errors = np.abs(y_pred_original - y_test_original) / y_test_original * 100
avg_percent_error = np.nanmean(percent_errors)
print(f"\n📉 平均误差百分比: {avg_percent_error:.2f}%")

# -------- 随机打印100条误差 -------- #
print("\n📌 随机抽取100条预测误差（百分比）:")
random_indices = np.random.choice(len(y_test_original), size=100, replace=False)
for i, idx in enumerate(random_indices):
    print(f"样本 {i+1}: 真实={y_test_original[idx]:.2f}, 预测={y_pred_original[idx]:.2f}, 误差={percent_errors[idx]:.2f}%")

# -------- 特征重要性分析 -------- #
print("\n📊 特征重要性分析（Feature Importance）:")

importances = best_model.feature_importances_
feature_names = X_train.columns
importance_df = pd.DataFrame({'Feature': feature_names, 'Importance': importances})
importance_df = importance_df.sort_values(by='Importance', ascending=False)

# 打印前20个最重要的特征
print(importance_df.head(20))

# 可视化前20个特征的重要性
plt.figure(figsize=(10, 8))
plt.barh(importance_df['Feature'][:20][::-1], importance_df['Importance'][:20][::-1], color='skyblue')
plt.xlabel('Importance', fontsize=12)
plt.title('Top 20 Feature Importances (XGBoost)', fontsize=14)
plt.grid(axis='x')
plt.tight_layout()
#plt.show()


# ---------- 可视化：预测结果 vs 实际值 ----------
# 设置分段数（控制最终曲线的点数）
n_segments = 100

# 划分数据并计算每段的均值（降噪处理）
segment_size = len(y_test_original) // n_segments
avg_true = []
avg_pred = []

for i in range(n_segments):
    start = i * segment_size
    end = (i + 1) * segment_size if i < n_segments - 1 else len(y_test_original)
    avg_true.append(np.mean(y_test_original[start:end]))
    avg_pred.append(np.mean(y_pred_original[start:end]))

# 可视化
plt.figure(figsize=(20, 10))
plt.plot(range(n_segments), avg_pred, label='Predicted Price', color='#299d8f', linestyle='-', linewidth=5)
plt.plot(range(n_segments), avg_true, label='Actual Price', color='#e66d50', linestyle='-', linewidth=5)
plt.title('XGBoost--Predicted vs Actual Housing Prices', fontsize=20)
plt.xlabel('Group Index', fontsize=16)
plt.ylabel('Average Price per Group', fontsize=16)
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()

end_time = time.time()  # ✅ 程序结束计时
elapsed_time = end_time - start_time
print(f"\n⏱️ 脚本总运行时间：{elapsed_time:.2f} 秒")




