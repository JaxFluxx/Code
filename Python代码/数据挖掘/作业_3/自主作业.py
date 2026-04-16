# 导入必要的库以进行数据处理、可视化和模型构建
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import classification_report, confusion_matrix


plt.rcParams['font.sans-serif'] = ['Arial Unicode MS']  # 苹果系统显示中文字体

# 读取水果数据集，并展示数据的前几行
data_path = 'fruit_data.csv'
data = pd.read_csv(data_path)
print(data.head())

# 特征和标签的选择
X = data[['mass', 'width', 'height', 'color_score']]
y = data['fruit_name']

# 划分数据集为训练集和测试集
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42)

# 对特征进行标准化以提高模型性能
scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

# 使用SVM模型进行分类
svm_model = SVC(kernel='rbf', C=1, gamma='scale')
svm_model.fit(X_train, y_train)
y_pred_svm = svm_model.predict(X_test)

# 使用KNN模型进行分类
knn_model = KNeighborsClassifier(n_neighbors=5)
knn_model.fit(X_train, y_train)
y_pred_knn = knn_model.predict(X_test)

# 使用决策树模型进行分类
tree_model = DecisionTreeClassifier(random_state=42)
tree_model.fit(X_train, y_train)
y_pred_tree = tree_model.predict(X_test)

# 打印分类报告并绘制混淆矩阵的热力图
def print_report_and_confusion_matrix(y_true, y_pred, model_name):
    print(f"Classification Report for {model_name}:")
    print(classification_report(y_true, y_pred))
    cm = confusion_matrix(y_true, y_pred)
    plt.figure(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Purples",
                xticklabels=np.unique(y), yticklabels=np.unique(y))
    plt.title(f"Confusion Matrix for {model_name}")
    plt.xlabel("预测")
    plt.ylabel("真实")
    plt.show()

# 显示SVM的分类结果
print_report_and_confusion_matrix(y_test, y_pred_svm, "SVM")

# 显示KNN的分类结果
print_report_and_confusion_matrix(y_test, y_pred_knn, "KNN")

# 显示决策树的分类结果
print_report_and_confusion_matrix(y_test, y_pred_tree, "决策树")
