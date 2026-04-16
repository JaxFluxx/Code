import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import RidgeCV
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error
from sklearn.model_selection import train_test_split
import lightgbm as lgb
import xgboost as xgb
from scipy.optimize import minimize
from tqdm import tqdm
import time

start_time = time.time()  # ✅ 程序开始计时

plt.rcParams['font.sans-serif'] = ['Arial Unicode MS']  # 苹果系统显示中文字体


# ----------- 基本设置 ----------- #
mean_price = 549.6649639920413
std_price = 343.7072939272807

train_path = '/Users/jia/Desktop/论文/数据/数据处理/北京二手房成交_1.9_train.csv'
test_path = '/Users/jia/Desktop/论文/数据/数据处理/北京二手房成交_1.9_test.csv'

tqdm.write("📥 正在读取数据...")
train_df = pd.read_csv(train_path)
test_df = pd.read_csv(test_path)

train_df = train_df.drop('id', axis=1)
test_df = test_df.drop('id', axis=1)

X_train = train_df.iloc[:, :-1]
y_train = train_df.iloc[:, -1]
X_test = test_df.iloc[:, :-1]
y_test = test_df.iloc[:, -1]

# ----------- 类别型特征转换 ----------- #
tqdm.write("🔄 正在转换类别变量为数值...")
for col in tqdm(X_train.columns, desc="编码类别变量"):
    if X_train[col].dtype == 'object':
        X_train[col] = X_train[col].astype('category').cat.codes
        X_test[col] = X_test[col].astype('category').cat.codes

# ----------- 模型定义 ----------- #
tqdm.write("🧱 构建并训练模型...")

# Random Forest
rf_model = RandomForestRegressor(
    n_estimators=200,
    max_depth=10,
    min_samples_split=2,
    min_samples_leaf=1,
    random_state=42,
    n_jobs=-1
)
rf_model.fit(X_train, y_train)

# LightGBM
lgb_model = lgb.LGBMRegressor(
    n_estimators=150,
    max_depth=-1,
    learning_rate=0.2,
    num_leaves=70,
    random_state=42
)
lgb_model.fit(X_train, y_train)

# XGBoost
xgb_model = xgb.XGBRegressor(
    n_estimators=400,
    max_depth=9,
    learning_rate=0.2,
    subsample=0.9,
    colsample_bytree=1,
    random_state=42,
    n_jobs=-1
)
xgb_model.fit(X_train, y_train)

# ----------- 预测与还原 ----------- #
y_pred_rf = rf_model.predict(X_test) * std_price + mean_price
y_pred_lgb = lgb_model.predict(X_test) * std_price + mean_price
y_pred_xgb = xgb_model.predict(X_test) * std_price + mean_price
y_test_original = y_test * std_price + mean_price

# ----------- 自动权重优化（最小 RMSE） ----------- #
tqdm.write("🔧 正在优化加权权重...")

preds = np.vstack([y_pred_rf, y_pred_lgb, y_pred_xgb]).T

def rmse_loss(weights):
    weighted_pred = np.dot(preds, weights)
    return np.sqrt(mean_squared_error(y_test_original, weighted_pred))

initial_weights = [1/3, 1/3, 1/3]
bounds = [(0, 1)] * 3
constraints = {'type': 'eq', 'fun': lambda w: np.sum(w) - 1}

result = minimize(rmse_loss, initial_weights, bounds=bounds, constraints=constraints)
opt_weights = result.x
final_pred = preds @ opt_weights

# ----------- 模型评估 ----------- #
r2 = r2_score(y_test_original, final_pred)
mae = mean_absolute_error(y_test_original, final_pred)
rmse = mean_squared_error(y_test_original, final_pred, squared=False)
mape = np.mean(np.abs((y_test_original - final_pred) / y_test_original)) * 100

tqdm.write("\n📊 加权集成模型评估：")
tqdm.write(f"最优权重: RF={opt_weights[0]:.3f}, LGB={opt_weights[1]:.3f}, XGB={opt_weights[2]:.3f}")
tqdm.write(f"R² Score: {r2:.4f}")
tqdm.write(f"MAE: {mae:.2f}")
tqdm.write(f"RMSE: {rmse:.2f}")
tqdm.write(f"MAPE: {mape:.2f}%")

# ----------- 可视化（预测 vs 实际，随机采样散点 vs 简化预测曲线） ----------- #
# ----------- 参数设置 ----------- #
group_count = 100
samples_per_group = 20
prediction_step = 20
y_marks = [200, 600, 1000, 1500]

# ----------- 排序与采样 ----------- #
sorted_index = np.argsort(y_test_original)
y_true_sorted = y_test_original[sorted_index]
y_pred_sorted = final_pred[sorted_index]

sample_indices = []
group_size = len(y_test_original) // group_count
for i in range(group_count):
    start = i * group_size
    end = (i + 1) * group_size if i < group_count - 1 else len(y_test_original)
    group_indices = np.random.choice(sorted_index[start:end], size=min(samples_per_group, end - start), replace=False)
    sample_indices.extend(group_indices)

scatter_x = np.where(np.isin(sorted_index, sample_indices))[0]
scatter_y = y_test_original[sample_indices]

x_pred_line = np.arange(0, len(y_pred_sorted), prediction_step)
y_pred_line = y_pred_sorted[x_pred_line]

# ----------- 绘图 ----------- #
plt.figure(figsize=(12, 6))

# 散点图
plt.scatter(scatter_x, scatter_y, label='Actual Price (Sampled)', color='#e66d50', alpha=0.6)

# 预测曲线
plt.plot(x_pred_line, y_pred_line, label='Weighted Ensemble Prediction (Sampled)', color='#299d8f', linestyle='-',
         linewidth=2)

# 标注 y 值点并连线
for y_val in y_marks:
    # 找到最接近 y_val 的点
    diffs = np.abs(y_pred_line - y_val)
    idx = np.argmin(diffs)
    x_val = x_pred_line[idx]
    y_actual = y_pred_line[idx]

    # 标记点
    plt.scatter(x_val, y_actual, color='black', zorder=5)

    # 添加文本注释，显示坐标 (x, y)
    plt.text(x_val + 5, y_actual + 20, f'({x_val}, {y_actual:.1f})', fontsize=10, color='black')

    # 画虚线到 x 轴和 y 轴
    plt.plot([x_val, x_val], [0, y_actual], linestyle='--', color='black', linewidth=1)
    plt.plot([0, x_val], [y_actual, y_actual], linestyle='--', color='black', linewidth=1)


# ----------- 坐标轴设置 ----------- #
plt.xlim(left=0)
plt.ylim(0, 4000)


# 只保留 y=0 的标签，不显示 x=0 的刻度
ax = plt.gca()
xticks = ax.get_xticks()
yticks = ax.get_yticks()
ax.set_xticks([tick for tick in xticks if tick != 0])
ax.set_yticks(yticks)  # 保留 y=0

plt.title('Ensemble Model Prediction vs Actual Price', fontsize=20)
plt.xlabel('Sample Index', fontsize=16)
plt.ylabel('Price (×10,000 RMB)', fontsize=16)
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()


# ----------- 模型 RMSE 比较图 ----------- #
rmse_values = [
    mean_squared_error(y_test_original, y_pred_rf, squared=False),
    mean_squared_error(y_test_original, y_pred_lgb, squared=False),
    mean_squared_error(y_test_original, y_pred_xgb, squared=False),
    rmse
]
models = ['RandomForest', 'LightGBM', 'XGBoost', 'Weighted Ensemble']

plt.figure(figsize=(8, 5))
plt.bar(models, rmse_values, color=['orange', 'lightgreen', 'dodgerblue', 'purple'])
plt.title("Model Comparison: RMSE", fontsize=16)
plt.ylabel("RMSE", fontsize=12)
plt.tight_layout()
# plt.show()

# ---------- 可视化：预测结果 vs 实际值 ----------
n_segments = 100
segment_size = len(y_test_original) // n_segments
avg_true = []
avg_pred = []

for i in range(n_segments):
    start = i * segment_size
    end = (i + 1) * segment_size if i < n_segments - 1 else len(y_test_original)
    avg_true.append(np.mean(y_test_original[start:end]))
    avg_pred.append(np.mean(final_pred[start:end]))

plt.figure(figsize=(20, 10))
plt.plot(range(n_segments), avg_pred, label='Predicted Price', color='#299d8f', linestyle='-', linewidth=5)
plt.plot(range(n_segments), avg_true, label='Actual Price', color='#e66d50', linestyle='-', linewidth=5)
plt.title('Ensemble model--Predicted vs Actual Housing Prices', fontsize=20)
plt.xlabel('Group Index', fontsize=16)
plt.ylabel('Average Price per Group', fontsize=16)
plt.legend()
plt.grid(True)
plt.tight_layout()
# plt.show()

end_time = time.time()
print(f"\n⏱️ 脚本总运行时间：{end_time - start_time:.2f} 秒")

# ----------- 打印测试集中的随机200条数据（含真实值、预测值、误差等） ----------- #
np.random.seed(42)  # 保证可重复
random_indices = np.random.choice(len(y_test_original), size=200, replace=False)

df_comparison = pd.DataFrame({
    'Actual Price': y_test_original[random_indices],
    'Predicted Price': final_pred[random_indices]
})

df_comparison['Absolute Error'] = np.abs(df_comparison['Actual Price'] - df_comparison['Predicted Price'])
df_comparison['Percentage Error (%)'] = (df_comparison['Absolute Error'] / df_comparison['Actual Price']) * 100

# 重置索引便于查看
df_comparison.reset_index(drop=True, inplace=True)

# 打印前20行查看效果（你可以改成200）
print("\n📋 随机200条测试样本的预测表现：")
print(df_comparison.head(200).to_string(index=False))  # 可改成 df_comparison.head(200)

