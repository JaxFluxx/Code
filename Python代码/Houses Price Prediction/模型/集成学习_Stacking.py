import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestRegressor, StackingRegressor
from sklearn.linear_model import RidgeCV
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error
from sklearn.model_selection import train_test_split
import lightgbm as lgb
import xgboost as xgb
from tqdm import tqdm

# 统一中文字体（Mac）
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS']

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

# ----------- 定义基础模型 ----------- #
tqdm.write("🧱 构建基础模型...")

# Random Forest 使用最佳参数
rf_model = RandomForestRegressor(
    bootstrap=True,
    ccp_alpha=0.0,
    criterion='squared_error',
    max_depth=None,
    max_features=1.0,
    max_leaf_nodes=None,
    max_samples=None,
    min_impurity_decrease=0.0,
    min_samples_leaf=1,
    min_samples_split=2,
    min_weight_fraction_leaf=0.0,
    monotonic_cst=None,
    n_estimators=100,
    n_jobs=-1,
    oob_score=False,
    random_state=42,
    verbose=0,
    warm_start=False
)

# LightGBM 模型训练
tqdm.write("🚀 正在训练 LightGBM 模型...")
lgb_model = lgb.LGBMRegressor(
    n_estimators=100,
    random_state=42
)
lgb_model.fit(
    X_train,
    y_train,
    eval_set=[(X_train, y_train)],
    eval_metric='l2',
    callbacks=[lgb.log_evaluation(period=10)]
)

# XGBoost 模型训练
tqdm.write("🚀 正在训练 XGBoost 模型...")
xgb_model = xgb.XGBRegressor(
    n_estimators=600,
    max_depth=11,
    learning_rate=0.3,
    subsample=0.9,
    colsample_bytree=1,
    random_state=42,
    n_jobs=-1
)
xgb_model.fit(X_train, y_train)

# ----------- 堆叠模型 ----------- #
tqdm.write("🧠 构建 Stacking 模型...")
stacking_model = StackingRegressor(
    estimators=[
        ('rf', rf_model),
        ('lgb', lgb_model),
        ('xgb', xgb_model)
    ],
    final_estimator=RidgeCV(),
    n_jobs=-1
)

# ----------- 训练堆叠模型 ----------- #
tqdm.write("🚀 正在训练 Stacking 模型...")
stacking_model.fit(X_train, y_train)

# ----------- 预测与还原 ----------- #
tqdm.write("🔍 正在预测...")
y_pred = stacking_model.predict(X_test)
y_pred_original = y_pred * std_price + mean_price
y_test_original = y_test * std_price + mean_price

# ----------- 评估 ----------- #
r2 = r2_score(y_test_original, y_pred_original)
mae = mean_absolute_error(y_test_original, y_pred_original)
rmse = mean_squared_error(y_test_original, y_pred_original, squared=False)

tqdm.write("\n📊 模型评估（Stacking）：")
tqdm.write(f"R² Score: {r2:.4f}")
tqdm.write(f"MAE: {mae:.2f}")
tqdm.write(f"RMSE: {rmse:.2f}")

# ----------- 可视化 ----------- #
tqdm.write("📈 正在绘图...")
sample_size = 100
sorted_index = np.argsort(y_test_original)
step = len(y_test_original) // sample_size
sample_indices = sorted_index[::step][:sample_size]

sample_true = y_test_original[sample_indices]
sample_pred = y_pred_original[sample_indices]

plt.figure(figsize=(12, 6))
plt.plot(range(sample_size), sample_true, label='Actual Price', color='green', linewidth=2)
plt.plot(range(sample_size), sample_pred, label='Predicted Price', color='blue', linestyle='--', linewidth=2)
plt.title('Stacking Prediction vs Actual Price (Sampled)', fontsize=16)
plt.xlabel('Sample Index', fontsize=12)
plt.ylabel('Price', fontsize=12)
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()

# ----------- 平均误差百分比 ----------- #
mape = np.mean(np.abs((y_test_original - y_pred_original) / y_test_original)) * 100
tqdm.write(f"平均绝对百分比误差: {mape:.2f}%")

# 计算各模型 RMSE
rmse_rf = mean_squared_error(y_test_original, rf_model.predict(X_test)*std_price + mean_price, squared=False)
rmse_lgb = mean_squared_error(y_test_original, lgb_model.predict(X_test)*std_price + mean_price, squared=False)
rmse_xgb = mean_squared_error(y_test_original, xgb_model.predict(X_test)*std_price + mean_price, squared=False)

# 绘图
models = ['RandomForest', 'LightGBM', 'XGBoost', 'Stacking']
rmse_values = [rmse_rf, rmse_lgb, rmse_xgb, rmse]

plt.figure(figsize=(8, 5))
plt.bar(models, rmse_values, color=['orange', 'lightgreen', 'dodgerblue', 'crimson'])
plt.title("Model Comparison: RMSE", fontsize=16)
plt.ylabel("RMSE", fontsize=12)
plt.tight_layout()
plt.show()
