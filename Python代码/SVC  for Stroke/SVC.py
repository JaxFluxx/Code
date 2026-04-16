import pandas as pd
from sklearn.svm import SVC
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix

# 1. 读取数据
train_path = r"/Users/jia/Desktop/学习 /科研/SVM_支持向量机/Dataset_cleaned/archive/healthcare_stroke_train.csv"
test_path = r"/Users/jia/Desktop/学习 /科研/SVM_支持向量机/Dataset_cleaned/archive/healthcare_stroke_test.csv"

df_train = pd.read_csv(train_path)
df_test = pd.read_csv(test_path)

# 2. 创建平衡的训练集：所有 stroke=1 和 350 随机的 stroke=0
stroke_1 = df_train[df_train['stroke'] == 1]
stroke_0 = df_train[df_train['stroke'] == 0].sample(n=350, random_state=42)
df_train_balanced = pd.concat([stroke_1, stroke_0], axis=0).sample(frac=1, random_state=42)

# 3. 分割特征和标签
X_train = df_train_balanced.drop('stroke', axis=1)
y_train = df_train_balanced['stroke']
X_test = df_test.drop('stroke', axis=1)
y_test = df_test['stroke']

# 4. 构建并训练 SVC 模型
svc_model = SVC(kernel='rbf', C=1.0, gamma='scale', random_state=42)
svc_model.fit(X_train, y_train)

# 5. 在训练集上评估
y_pred_train = svc_model.predict(X_train)
print("\n训练集准确率:", accuracy_score(y_train, y_pred_train))

# 6. 在测试集上评估

# print("测试集分类报告:")
# print(classification_report(y_test, y_pred_test))

# 7. 自定义格式化的分类报告（完整版）

# Evaluate predictions
y_pred_test = svc_model.predict(X_test)
report = classification_report(y_test, y_pred_test, output_dict=True)
accuracy = accuracy_score(y_test, y_pred_test)

# 打印分类报告
print("\n分类报告:")
print(f"{'':>18} {'precision':>10} {'recall':>10} {'f1-score':>10} {'support':>10}")

for label in ['0', '1']:
    row = report[label]
    name = 'Non-Stroke' if label == '0' else 'Stroke'
    print(f"{name:>18} {row['precision']:10.2f} {row['recall']:10.2f} {row['f1-score']:10.2f} {row['support']:10.0f}")

# 准确率行
print(f"\n{'accuracy':>18} {'':>10} {'':>10} {accuracy:10.2f} {sum([report['0']['support'], report['1']['support']]):10.0f}")

# 宏平均
macro = report['macro avg']
print(f"{'macro avg':>18} {macro['precision']:10.2f} {macro['recall']:10.2f} {macro['f1-score']:10.2f} {macro['support']:10.0f}")

# 加权平均
weighted = report['weighted avg']
print(f"{'weighted avg':>18} {weighted['precision']:10.2f} {weighted['recall']:10.2f} {weighted['f1-score']:10.2f} {weighted['support']:10.0f}")

# 打印混淆矩阵
conf_matrix = confusion_matrix(y_test, y_pred_test)
print("\n混淆矩阵:")
print(conf_matrix)

# 打印测试集准确率
print("\n测试集准确率:", accuracy_score(y_test, y_pred_test))
