# 步骤1：加载手写数字数据集并将数据集划分为训练集和测试集，创建包含1000棵树的随机森林分类器，使用训练数据进行模型训练，并对测试集进行预测。
# 步骤2：输出分类报告，展示模型的性能指标，包括精度、召回率、F1分数等。
# 步骤3：计算混淆矩阵并绘制热力图，通过颜色直观展示模型的预测准确性和错误分布。

# lab3_3_2
import numpy as np
import matplotlib.pyplot as plt
from sklearn.datasets import load_digits     #用于加载手写数字数据集
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn import metrics
from sklearn.metrics import confusion_matrix
import seaborn as sns

plt.rcParams['font.sans-serif'] = ['Arial Unicode MS'] #苹果系统显示中文字体

digits = load_digits()  # 加载手写数字数据集
digits.keys()  #查看数据集的键

#展示前64个手写数字图像
fig = plt.figure(figsize=(6, 6))
fig.subplots_adjust(left=0, right=1, bottom=0, top=1, hspace=0.05, wspace=0.05)

#画出前64个手写数字图像
for i in range(64):
    ax = fig.add_subplot(8, 8, i + 1, xticks=[], yticks=[])
    ax.imshow(digits.images[i], cmap=plt.cm.binary, interpolation='nearest')
    ax.text(0, 7, str(digits.target[i]))  #标注数字标签

plt.show()

# 1）将数据集分为训练集和测试集，创建随机森林分类器并训练模型
X_train, X_test, y_train, y_test = train_test_split(
    digits.data, digits.target, test_size=0.25, random_state=0)  #分割数据集，75%训练集，25%测试集

rf_model = RandomForestClassifier(n_estimators=1000, random_state=0)  # 初始化1000棵决策树的随机森林
rf_model.fit(X_train, y_train)  #训练模型

y_pred = rf_model.predict(X_test)  # 使用训练好的模型预测测试集标签

# 2）打印分类报告，显示精度、召回率和F1分数
print("分类结果\n")
print(metrics.classification_report(y_test, y_pred))

# 3）计算混淆矩阵并绘制热力图
conf_matrix = confusion_matrix(y_test, y_pred)  #计算混淆矩阵
plt.figure(figsize=(8, 6))
sns.heatmap(conf_matrix, annot=True, fmt="d", cmap="Greens")


plt.xlabel("预测")  # 横轴为预测标签
plt.ylabel("真实")  # 纵轴为真实标签
plt.title("随机森林分类器混淆矩阵")
plt.show()
