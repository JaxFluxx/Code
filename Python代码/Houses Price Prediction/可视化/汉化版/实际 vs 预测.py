# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import lightgbm as lgb
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error
from sklearn.model_selection import GridSearchCV
import time
import random

# ======================
# 0. 全局设置与定时
# ======================
start_time = time.time()

SEED = 42
np.random.seed(SEED)
random.seed(SEED)

plt.rcParams['font.sans-serif'] = ['Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False

# ======================
# 1. 数据读取
# ======================
train_df = pd.read_csv(
    r'/Users/jia/Desktop/学习 /论文/数据/数据处理/北京二手房成交_1.9_train.csv',
    encoding='utf-8'
)
test_df = pd.read_csv(
    r'/Users/jia/Desktop/学习 /论文/数据/数据处理/北京二手房成交_1.9_test.csv',
    encoding='utf-8'
)

# ======================
# 2. 标准化信息
# ======================
MEAN_PRICE = 549.6649639920413
STD_PRICE  = 343.7072939272807
TARGET_COL = '价格'
DROP_COLS  = ['id']

# 删除无用列
train_df = train_df.drop(columns=[c for c in DROP_COLS if c in train_df.columns], errors='ignore')
test_df  = test_df.drop(columns=[c for c in DROP_COLS if c in test_df.columns], errors='ignore')

# 特征和标签
X_train = train_df.drop(columns=[TARGET_COL])
y_train = train_df[TARGET_COL].astype(float)
X_test  = test_df.drop(columns=[TARGET_COL])
y_test  = test_df[TARGET_COL].astype(float)
X_test  = X_test[X_train.columns]

# ======================
# 3. 判断是否标准化
# ======================
def looks_standardized(series: pd.Series) -> bool:
    m = float(series.mean())
    s = float(series.std(ddof=0))
    return (abs(m) < 0.5) and (0.5 < s < 2.0)

y_train_is_std = looks_standardized(y_train)
y_test_is_std  = looks_standardized(y_test)

# ======================
# 4. 训练 LightGBM
# ======================
params = dict(
    objective='regression',
    metric='rmse',
    n_estimators=150,
    learning_rate=0.08,
    max_depth=-1,
    num_leaves=70,
    subsample=0.9,
    colsample_bytree=0.9,
    random_state=SEED,
    n_jobs=-1
)
model = lgb.LGBMRegressor(**params)
model.fit(X_train, y_train)

# ======================
# 5. 预测与还原
# ======================
y_pred = model.predict(X_test)

def restore(series, is_std):
    return series * STD_PRICE + MEAN_PRICE if is_std else series

y_test_original = restore(y_test.values, y_test_is_std)
y_pred_original = restore(y_pred, y_test_is_std)

# ======================
# 6. 评估
# ======================
def rmse(a, b): return np.sqrt(mean_squared_error(a, b))
print("—— 模型评估（单位：万元）——")
print(f"R²   : {r2_score(y_test_original, y_pred_original):.4f}")
print(f"MAE  : {mean_absolute_error(y_test_original, y_pred_original):.2f}")
print(f"RMSE : {rmse(y_test_original, y_pred_original):.2f}")

# ======================
# 7. 可视化
# ======================
n_segments = 100
n = len(y_test_original)
segment_size = max(1, n // n_segments)

avg_true, avg_pred = [], []
for i in range(n_segments):
    s = i * segment_size
    e = (i + 1) * segment_size if i < n_segments - 1 else n
    avg_true.append(np.mean(y_test_original[s:e]))
    avg_pred.append(np.mean(y_pred_original[s:e]))

plt.figure(figsize=(20, 10))
plt.plot(range(n_segments), avg_pred, label='预测价格（组均值）', color='#299d8f', linewidth=5)
plt.plot(range(n_segments), avg_true, label='实际价格（组均值）', color='#e66d50', linewidth=5)
plt.title('LightGBM：分组均值对比（预测 vs 实际）', fontsize=22, fontweight='bold')
plt.xlabel('分组索引', fontsize=16, fontweight='bold')
plt.ylabel('每组平均价格（万元）', fontsize=16, fontweight='bold')
plt.legend(fontsize=14)
plt.grid(True, axis='y', linestyle='--', alpha=0.6)
plt.tight_layout()
plt.show()

# ======================
# 8. 运行时间
# ======================
print(f"\n⏱️ 脚本总运行时间：{time.time()-start_time:.2f} 秒")
