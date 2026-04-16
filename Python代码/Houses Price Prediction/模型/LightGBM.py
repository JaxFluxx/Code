import pandas as pd
import lightgbm as lgb
import matplotlib.pyplot as plt
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error
import numpy as np
import random
import time  # ✅ 添加时间模块
from sklearn.model_selection import GridSearchCV

start_time = time.time()  # ✅ 程序开始计时


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

# ---------- 模型训练 ---------- #

# ---------- 网格搜索 ---------- #
print("🔍 正在进行网格搜索以优化超参数...")

# 定义参数网格
param_grid = {
    'num_leaves': [31, 50],
    'learning_rate': [0.1, 0.05],
    'n_estimators': [100, 200],
    'max_depth': [ -1, 10, 20]
}

# 初始化模型
lgb_model = lgb.LGBMRegressor(random_state=42)

# 使用 GridSearchCV
grid_search = GridSearchCV(
    estimator=lgb_model,
    param_grid=param_grid,
    cv=3,  # 3折交叉验证
    scoring='neg_mean_squared_error',  # 使用负均方误差进行评价
    verbose=2,
    n_jobs=-1  # 使用所有可用 CPU 核
)

# 拟合训练集
grid_search.fit(X_train, y_train)

# 输出最佳参数和得分
print(f"\n✅ 最佳参数: {grid_search.best_params_}")
print(f"✅ 最佳得分 (负MSE): {grid_search.best_score_:.4f}")

# 使用最佳参数创建最终模型
model = grid_search.best_estimator_


# ---------- 模型预测 ---------- #
print("🔍 正在进行预测...")
y_pred = model.predict(X_test)

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
    true_price = y_test_original[i]
    pred_price = y_pred_original[i]
    percent_error = abs(pred_price - true_price) / true_price * 100 if true_price != 0 else float('nan')
    percent_errors.append(percent_error)

# 平均误差百分比
average_percent_error = np.nanmean(percent_errors)
print(f"\n📉 平均预测误差百分比: {average_percent_error:.2f}%")

# 随机打印 100 条预测误差
print("\n🔢 随机抽取 100 条预测误差（相对真实房价百分比）：")
sample_indices = random.sample(range(len(percent_errors)), min(100, len(percent_errors)))
for i in sample_indices:
    print(f"样本 {i + 1}: 真实={y_test_original[i]:.2f}, 预测={y_pred_original[i]:.2f}, 误差={percent_errors[i]:.2f}%")


# ---------- 特征重要性可视化 ---------- #
print("\n📌 正在绘制特征重要性图...")

# 获取特征名称和对应的重要性
feature_names = X_train.columns
importances = model.feature_importances_

# 构建 DataFrame 并按重要性排序
importance_df = pd.DataFrame({'Feature': feature_names, 'Importance': importances})
importance_df = importance_df.sort_values(by='Importance', ascending=False)

# 可视化
plt.figure(figsize=(10, 8))
bars = plt.barh(importance_df['Feature'], importance_df['Importance'], color='skyblue')
plt.gca().invert_yaxis()  # 重要性高的在上面
plt.title('Feature Importance', fontsize=16)
plt.xlabel('Importance Score', fontsize=12)
plt.tight_layout()
plt.grid(axis='x', linestyle='--', alpha=0.7)

# 在每根柱子上添加数值标签
for bar in bars:
    width = bar.get_width()
    plt.text(width + 1, bar.get_y() + bar.get_height() / 2,
             f'{int(width)}', va='center', fontsize=10)

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
plt.title('LightGBM--Predicted vs Actual Housing Prices', fontsize=20)
plt.xlabel('Group Index', fontsize=16)
plt.ylabel('Average Price per Group', fontsize=16)
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()

end_time = time.time()  # ✅ 程序结束计时
elapsed_time = end_time - start_time
print(f"\n⏱️ 脚本总运行时间：{elapsed_time:.2f} 秒")

