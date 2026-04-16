import pandas as pd
from sklearn.svm import SVC
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix
from sklearn.feature_selection import SelectKBest, f_classif
import matplotlib.pyplot as plt
from imblearn.over_sampling import SMOTE
from sklearn.calibration import CalibratedClassifierCV
from tqdm import tqdm
import time

# 1. 正确读取训练集和测试集
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

# 可视化 F-score（按重要性排序）
sorted_idx = scores.argsort()[::-1]
plt.figure(figsize=(12, 6))
plt.bar([X_train_full.columns[i] for i in sorted_idx], scores[sorted_idx])
plt.xticks(rotation=90)
plt.title("Sorted Feature Importance Scores (ANOVA F-score)")
plt.tight_layout()
# plt.show()

# 6. 判断是否建议 PCA
low_score_features = sum(score < 1.0 for score in scores)
if low_score_features > len(scores) // 2:
    print("很多特征得分低，建议尝试 PCA 或特征选择")
else:
    print("大部分特征得分较高，目前可先不使用 PCA")

# 7. 拆分训练/验证集（注意验证集不做 SMOTE）
X_train, X_val, y_train, y_val = train_test_split(X_train_full, y_train_full, test_size=0.2, random_state=42)

# 8. 过采样处理（只对训练集进行 SMOTE）
print("\n正在进行 SMOTE 过采样处理...")
smote = SMOTE(random_state=42)
X_train_resampled, y_train_resampled = smote.fit_resample(X_train, y_train)
print("SMOTE 完成：", X_train_resampled.shape, y_train_resampled.value_counts().to_dict())

# 9. 模拟训练进度条
print("\n正在训练 SVC 模型（带 class_weight=balanced + 校准）...")
for _ in tqdm(range(100), desc="训练中", ncols=100):
    time.sleep(0.005)

# 10. 构建并训练模型 + 校准
svc_base = SVC(kernel='rbf', C=1.0, gamma='scale', class_weight='balanced', probability=True)
svc_model = CalibratedClassifierCV(estimator=svc_base, method='sigmoid', cv=5)

svc_model.fit(X_train_resampled, y_train_resampled)
print("模型训练完成！")

# 11. 在训练/验证集上的表现
y_pred_train = svc_model.predict(X_train)
y_pred_val = svc_model.predict(X_val)

print("\n训练集准确率：", accuracy_score(y_train, y_pred_train))
print("验证集准确率：", accuracy_score(y_val, y_pred_val))
print("\n验证集分类报告：")
print(classification_report(y_val, y_pred_val))
print("混淆矩阵（验证集）：")
print(confusion_matrix(y_val, y_pred_val))

# 12. 在测试集上的表现
y_pred_test = svc_model.predict(X_test)
print("\n测试集准确率：", accuracy_score(y_test, y_pred_test))
print("\n测试集分类报告：")
print(classification_report(y_test, y_pred_test))
print("混淆矩阵（测试集）：")
print(confusion_matrix(y_test, y_pred_test))

# 13. 可选：输出预测概率（便于画 ROC / PR 曲线等）
# y_proba_test = svc_model.predict_proba(X_test)[:, 1]
