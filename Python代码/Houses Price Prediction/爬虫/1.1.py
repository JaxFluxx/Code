import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline

# 1. 定义数据路径（完整数据集）
data_path = r"/Users/jia/Desktop/学习 /科研/独立论文部分/朝阳二手房数据_贝壳网_清洗后.test.csv"

# 2. 读取数据
df = pd.read_csv(data_path)

# 3. 提取“室”和“厅”数量
df[['室', '厅']] = df['户型'].str.extract(r'(\d+)室(\d+)厅').astype(int)

# 4. 筛选特征
features = ['面积(平米)', '室', '厅', '建成年代', '经度', '纬度', '区域']
target = '价格(万元)'

X = df[features]
y = df[target]

# 5. 类别特征（区域）独热编码
categorical_features = ['区域']
numeric_features = ['面积(平米)', '室', '厅', '建成年代', '经度', '纬度']

# 6. 建立预处理器
preprocessor = ColumnTransformer(
    transformers=[
        ('cat', OneHotEncoder(handle_unknown='ignore'), categorical_features)
    ],
    remainder='passthrough'
)

# 7. 划分训练集和测试集（8:2）
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# 8. 构建管道 + 线性回归模型
model = Pipeline(steps=[
    ('preprocessor', preprocessor),
    ('regressor', LinearRegression())
])

# 9. 模型训练
model.fit(X_train, y_train)

# 10. 模型预测
y_pred = model.predict(X_test)

# 11. 评估结果
print(f'R² score: {r2_score(y_test, y_pred):.4f}')
print(f'MAE: {mean_absolute_error(y_test, y_pred):.2f}')
print(f'RMSE: {np.sqrt(mean_squared_error(y_test, y_pred)):.2f}')
