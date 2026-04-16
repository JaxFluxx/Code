import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error
from sklearn.model_selection import GridSearchCV
import time

start_time = time.time()  # ✅ 程序开始计时

plt.rcParams['font.sans-serif'] = ['Arial Unicode MS']  # 苹果系统显示中文字体

# 价格归一化的关键数据
mean_price = 549.6649639920413
std_price = 343.7072939272807

# 路径设置
train_path = '/Users/jia/Desktop/论文/数据/数据处理/北京二手房成交_1.9_train.csv'
test_path = '/Users/jia/Desktop/论文/数据/数据处理/北京二手房成交_1.9_test.csv'

# 读取数据
train_df = pd.read_csv(train_path)
test_df = pd.read_csv(test_path)

# 移除 id 列
train_df = train_df.drop('id', axis=1)
test_df = test_df.drop('id', axis=1)

# 分离特征和标签
X_train = train_df.iloc[:, :-1]
y_train = train_df.iloc[:, -1]
X_test = test_df.iloc[:, :-1]
y_test = test_df.iloc[:, -1]

# 将非数值型数据转为类别编码（Label Encoding）
for col in X_train.columns:
    if X_train[col].dtype == 'object':
        X_train[col] = X_train[col].astype('category').cat.codes
        X_test[col] = X_test[col].astype('category').cat.codes

# ---------- ✅ 网格搜索 ----------
param_grid = {
    'n_estimators': [100, 200],
    'max_depth': [10, 20, None],
    'min_samples_split': [2, 5],
    'min_samples_leaf': [1, 2]
}

print("⏳ 正在进行超参数搜索（GridSearchCV）...")
grid_search = GridSearchCV(RandomForestRegressor(random_state=42),
                           param_grid,
                           cv=3,
                           n_jobs=-1,
                           verbose=1,
                           scoring='neg_mean_squared_error')

grid_search.fit(X_train, y_train)
best_model = grid_search.best_estimator_

print("\n✅ 最佳参数组合：")
print(grid_search.best_params_)

# 预测
y_pred = best_model.predict(X_test)

# 还原预测和真实价格
y_pred_original = y_pred * std_price + mean_price
y_test_original = y_test * std_price + mean_price

# 模型评估
r2 = r2_score(y_test_original, y_pred_original)
mae = mean_absolute_error(y_test_original, y_pred_original)
rmse = mean_squared_error(y_test_original, y_pred_original, squared=False)

print("\n模型评估（Random Forest）：")
print(f"R² Score: {r2:.4f}")
print(f"MAE（平均绝对误差）: {mae:.2f}")
print(f"RMSE（均方根误差）: {rmse:.2f}")

# ---------- 可视化：预测结果 vs 实际值 ----------
n_segments = 100
segment_size = len(y_test_original) // n_segments
avg_true = []
avg_pred = []

for i in range(n_segments):
    start = i * segment_size
    end = (i + 1) * segment_size if i < n_segments - 1 else len(y_test_original)
    avg_true.append(np.mean(y_test_original[start:end]))
    avg_pred.append(np.mean(y_pred_original[start:end]))

plt.figure(figsize=(20, 10))
plt.plot(range(n_segments), avg_pred, label='Predicted Price', color='#299d8f', linestyle='-', linewidth=5)
plt.plot(range(n_segments), avg_true, label='Actual Price', color='#e66d50', linestyle='-', linewidth=5)
plt.title('Random Forest--Predicted vs Actual Housing Prices', fontsize=20)
plt.xlabel('Group Index', fontsize=16)
plt.ylabel('Average Price per Group', fontsize=16)
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()

end_time = time.time()
print(f"\n⏱️ 脚本总运行时间：{end_time - start_time:.2f} 秒")
