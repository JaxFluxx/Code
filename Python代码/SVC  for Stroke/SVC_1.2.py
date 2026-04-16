import pandas as pd
from sklearn.svm import SVC
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix, f1_score
from sklearn.feature_selection import SelectKBest, f_classif
import matplotlib.pyplot as plt
import seaborn as sns
from tqdm import tqdm
import time

# 1. 正确读取训练集和测试集（注意路径中空格）
train_path = r"/Users/jia/Desktop/学习 /科研/SVM_支持向量机/Dataset_cleaned/archive/healthcare_stroke_train.csv"
test_path = r"/Users/jia/Desktop/学习 /科研/SVM_支持向量机/Dataset_cleaned/archive/healthcare_stroke_test.csv"

df_train = pd.read_csv(train_path)
df_test = pd.read_csv(test_path)

# 2. 预览数据
print("训练集预览（前5行）：")
print(df_train.head())

# 3. 拆分特征和标签
X_train_full = df_train.drop('stroke', axis=1)
y_train_full = df_train['stroke']
X_test = df_test.drop('stroke', axis=1)
y_test = df_test['stroke']




# 4. 特征数量
print(f"\n特征维度：{X_train_full.shape[1]} 个特征")

# 5. 特征重要性分析（ANOVA F-score）
selector = SelectKBest(score_func=f_classif, k='all')
selector.fit(X_train_full, y_train_full)
scores = selector.scores_

# 可视化 F-score
plt.figure(figsize=(12, 6))
plt.bar(X_train_full.columns, scores)
plt.xticks(rotation=90)
plt.title("Feature Importance Scores (ANOVA F-score)")
plt.tight_layout()
# plt.show()

# 6. 判断是否建议 PCA
low_score_features = sum(score < 1.0 for score in scores)
if low_score_features > len(scores) // 2:
    print("很多特征得分低，建议尝试 PCA 或特征选择")
else:
    print("大部分特征得分较高，目前可先不使用 PCA")

# 7. 拆分训练/验证集
X_train, X_val, y_train, y_val = train_test_split(X_train_full, y_train_full, test_size=0.2, random_state=42)

# 8. 模拟训练进度条
print("\n正在训练 SVC 模型（带 class_weight=balanced）...")
for _ in tqdm(range(100), desc="训练中", ncols=100):
    time.sleep(0.005)

# 9. 构建并训练模型（重点优化）
svc_model = SVC(kernel='rbf', C=1.0, gamma='scale', class_weight='balanced')
svc_model.fit(X_train, y_train)
print("模型训练完成！")

# 10. 在训练/验证集上的表现
y_pred_train = svc_model.predict(X_train)
y_pred_val = svc_model.predict(X_val)

print("\n训练集准确率：", accuracy_score(y_train, y_pred_train))
print("验证集准确率：", accuracy_score(y_val, y_pred_val))
print("\n验证集分类报告：")
print(classification_report(y_val, y_pred_val))
print("混淆矩阵（验证集）：")
print(confusion_matrix(y_val, y_pred_val))
# 验证集 F1 分数
val_f1 = f1_score(y_val, y_pred_val)
print("验证集 F1 分数：", val_f1)

# 11. 在测试集上的表现
y_pred_test = svc_model.predict(X_test)
print("\n测试集准确率（整体召回率）：", accuracy_score(y_test, y_pred_test))
print("\n测试集分类报告：")
print(classification_report(y_test, y_pred_test))
print("混淆矩阵（测试集）：")
print(confusion_matrix(y_test, y_pred_test))
# 测试集 F1 分数
test_f1 = f1_score(y_test, y_pred_test)
print("测试集 F1 分数：", test_f1)
