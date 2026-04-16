import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.svm import SVC
from sklearn.metrics import classification_report, accuracy_score
import numpy as np

# 1. 读取原始数据（未标准化版本）
data_path = r"/Users/jia/Desktop/学习 /科研/SVM_支持向量机/Dataset_cleaned/archive/healthcare-dataset-stroke-data-cleaned.csv"
df = pd.read_csv(data_path)

# 2. 打乱数据
df = df.sample(frac=1, random_state=42).reset_index(drop=True)

# 3. 拆分特征和标签
X = df.drop(columns="stroke")
y = df["stroke"]

# 4. 拆分训练集和测试集（8:2）
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 5. 类别变量和数值变量列
categorical_features = ['gender', 'ever_married', 'work_type', 'Residence_type', 'smoking_status']
numeric_features = ['age', 'hypertension', 'heart_disease', 'avg_glucose_level', 'bmi']

# 6. 创建预处理器：对类别变量进行独热编码
preprocessor = ColumnTransformer(
    transformers=[
        ('cat', OneHotEncoder(handle_unknown='ignore'), categorical_features)
    ],
    remainder='passthrough'  # 其余数值列保持原样
)

# 7. 构建 SVC 模型流水线（未标准化）
model = Pipeline(steps=[
    ('preprocessor', preprocessor),
    ('classifier', SVC(kernel='rbf', C=1.0, gamma='scale'))
])

# 8. 模型训练
model.fit(X_train, y_train)
print("✅ 模型训练完成")

# 9. 测试集预测与评估
y_pred = model.predict(X_test)
print("\n📊 测试集准确率：", accuracy_score(y_test, y_pred))
print("📄 测试集分类报告：")
print(classification_report(y_test, y_pred))
