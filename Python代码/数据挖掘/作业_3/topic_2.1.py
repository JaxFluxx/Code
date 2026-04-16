# Lab3_2_1
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn import datasets
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.svm import SVC
from sklearn.metrics import classification_report, confusion_matrix

plt.rcParams['font.sans-serif'] = ['Arial Unicode MS']  # 苹果系统显示中文字体

# 加载鸢尾花数据集
iris = datasets.load_iris()
X = iris.data  # 花萼和花瓣的长度与宽度
y = iris.target  #表示鸢尾花的类别

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)  #将数据分为训练集和测试集，测试集占30%

#向量机的超参数网格，用于寻找最佳的参数组合
#C为正则化参数，kernel为核函数类型，gamma为核系数
param_grid = {'C': [0.1, 1, 10, 100], 'kernel': ['linear', 'rbf', 'poly'], 'gamma': [1, 0.1, 0.01, 0.001]}

#网格搜索选择最佳参数组合
grid_search = GridSearchCV(SVC(), param_grid, refit=True, verbose=2, cv=5)

#在训练集上拟合模型，同时寻找最佳超参数组合
grid_search.fit(X_train, y_train)

#使用最佳参数组合的SVM模型对测试集进行预测
y_pred = grid_search.predict(X_test)

#输出分类报告，包括精确率、召回率和F1分数等指标
print("Classification Report:")
print(classification_report(y_test, y_pred))

#混淆矩阵，比较真实标签与预测标签
cm = confusion_matrix(y_test, y_pred)
print("Confusion Matrix:")
print(cm)

#混淆矩阵的热力图
plt.figure(figsize=(8, 6))
sns.heatmap(cm, annot=True, fmt="d", cmap="Oranges",
            xticklabels=iris.target_names, yticklabels=iris.target_names)
plt.xlabel("Predicted Labels")
plt.ylabel("True Labels")
plt.title("Confusion Matrix")
plt.show()
