import pandas as pd
from sklearn.svm import SVC
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import precision_score, recall_score, f1_score, classification_report
import matplotlib.pyplot as plt
from sklearn.metrics import roc_curve, auc, confusion_matrix, ConfusionMatrixDisplay
from sklearn.preprocessing import label_binarize
import numpy as np


# 路径
train_path = r'/Users/jia/Desktop/学习 /机器学习/数据/train_1.5.csv'
test_path = r'/Users/jia/Desktop/学习 /机器学习/数据/test_1.5.csv'

# 读取全部数据
train_df = pd.read_csv(train_path)
test_df = pd.read_csv(test_path)

# 随机抽取数据（shuffle后取前n条）
train_df = train_df.sample(frac=1, random_state=42).reset_index(drop=True).iloc[:240000]
test_df = test_df.sample(frac=1, random_state=42).reset_index(drop=True).iloc[:60000]

target_col = 'Payment_Code'

# 准备训练和测试特征与标签
X_train = train_df.drop(columns=[target_col])
y_train = train_df[target_col]
X_test = test_df.drop(columns=[target_col])
y_test = test_df[target_col]

# 标签编码
le = LabelEncoder()
y_train_enc = le.fit_transform(y_train)
y_test_enc = le.transform(y_test)

# 创建SVM模型
svm_clf = SVC(kernel='rbf', probability=True, random_state=42)

# 训练模型
print("Training SVM model...")
svm_clf.fit(X_train, y_train_enc)
print("Training completed.")

print("模型参数：")
print(f"C = {svm_clf.C}")
print(f"gamma = {svm_clf._gamma}")
print(f"kernel = {svm_clf.kernel}")


# 预测测试集
y_pred = svm_clf.predict(X_test)


# 评估指标
precision = precision_score(y_test_enc, y_pred, average='weighted')
recall = recall_score(y_test_enc, y_pred, average='weighted')
f1 = f1_score(y_test_enc, y_pred, average='weighted')

# 转换target_names为字符串，避免TypeError
target_names = [str(c) for c in le.classes_]

print("\nClassification Report:")
print(classification_report(y_test_enc, y_pred, target_names=target_names))
print(f"Weighted Precision: {precision:.4f}")
print(f"Weighted Recall:    {recall:.4f}")
print(f"Weighted F1-score:  {f1:.4f}")


# ----------------------- 混淆矩阵 -----------------------
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay
import matplotlib.pyplot as plt

# 绘制混淆矩阵
cm = confusion_matrix(y_test_enc, y_pred)
disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=le.classes_)
disp.plot(cmap=plt.cm.Blues)
plt.title("Confusion Matrix")
plt.show()

# ----------------------- ROC 曲线（自动支持二分类和多分类） -----------------------
from sklearn.preprocessing import label_binarize
from sklearn.metrics import roc_curve, auc

# 获取每一类的预测概率
y_score = svm_clf.predict_proba(X_test)
n_classes = len(le.classes_)

# 判断是否为二分类或多分类
if n_classes == 2:
    # 二分类情况
    fpr, tpr, _ = roc_curve(y_test_enc, y_score[:, 1])
    roc_auc = auc(fpr, tpr)

    plt.figure(figsize=(6, 5))
    plt.plot(fpr, tpr, color='darkorange',
             label=f'ROC curve (AUC = {roc_auc:.2f})')
    plt.plot([0, 1], [0, 1], color='navy', linestyle='--')
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title('Binary ROC Curve')
    plt.legend(loc="lower right")
    plt.grid(True)
    plt.show()
else:
    # 多分类情况
    y_test_bin = label_binarize(y_test_enc, classes=range(n_classes))
    fpr = dict()
    tpr = dict()
    roc_auc = dict()

    for i in range(n_classes):
        fpr[i], tpr[i], _ = roc_curve(y_test_bin[:, i], y_score[:, i])
        roc_auc[i] = auc(fpr[i], tpr[i])

    plt.figure(figsize=(8, 6))
    colors = plt.cm.get_cmap("tab10", n_classes)

    for i in range(n_classes):
        plt.plot(fpr[i], tpr[i],
                 label=f'Class {le.classes_[i]} (AUC = {roc_auc[i]:.2f})',
                 color=colors(i))

    plt.plot([0, 1], [0, 1], 'k--', lw=1)
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title('Multiclass ROC Curve')
    plt.legend(loc="lower right")
    plt.grid(True)
    plt.show()
