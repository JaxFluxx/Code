# Lab3_2_2

# 数据导入及图像输出简单示例
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
from sklearn.datasets import fetch_lfw_people

plt.rcParams['font.sans-serif'] = ['Arial Unicode MS']  # 苹果系统显示中文字体

# 函数加载LFW数据集，min_faces_per_person=60 表示只保留至少有60张图片的人的数据。
faces = fetch_lfw_people(min_faces_per_person=60)
# 输出人名列表
print(faces.target_names)
# 输出图像的形状
print(faces.images.shape)

# 创建一个 3x5 的网格，展示 15 张人脸图像，ax.flat 是一个可以逐一遍历每个子图的扁平化数组。每个子图显示一张图片，并在下方标注人名。
fig, ax = plt.subplots(3, 5, figsize=(8, 6))
for i, axi in enumerate(ax.flat):
    axi.imshow(faces.images[i], cmap='bone')
    axi.set(xticks=[], yticks=[],
            xlabel=faces.target_names[faces.target[i]])

from sklearn.svm import SVC
from sklearn.decomposition import PCA
from sklearn.pipeline import make_pipeline

# 1）使用PCA进行降维和特征标准化，并使用径向基函数核的SVM分类
pca = PCA(n_components=150, whiten=True, random_state=42)  # PCA降维至150维，并标准化特征
svc = SVC(kernel='rbf', class_weight='balanced')  # 使用RBF核的SVM，并根据类别平衡调整权重
model = make_pipeline(pca, svc)  # 使用流水线将PCA和SVM组合

from sklearn.model_selection import train_test_split

# 2）将数据划分为训练集和测试集，测试集占比为25%，随机种子设为42
Xtrain, Xtest, ytrain, ytest = train_test_split(faces.data, faces.target, test_size=0.25, random_state=42)

from sklearn.model_selection import GridSearchCV

# 3）定义超参数网格，调整SVM的C和gamma参数
param_grid = {'svc__C': [1, 5, 10, 50], 'svc__gamma': [0.0001, 0.0005, 0.001, 0.005]}
# 使用GridSearchCV进行网格搜索，使用5折交叉验证
grid = GridSearchCV(model, param_grid, cv=5)
# 在训练集上进行网格搜索
grid.fit(Xtrain, ytrain)
# 输出最佳参数组合
print("Best parameters found:", grid.best_params_)

# 4）使用最佳参数组合训练的模型进行预测
best_model = grid.best_estimator_  # 提取最佳模型
yfit = best_model.predict(Xtest)  # 使用最佳模型对测试集进行预测

# 5）显示24张测试集人脸图像，并标注预测结果；预测错误的用红色标注
fig, ax = plt.subplots(4, 6, figsize=(12, 9))  # 设置图形网格，显示24张人脸
for i, axi in enumerate(ax.flat):
    axi.imshow(Xtest[i].reshape(62, 47), cmap='bone')  # 显示人脸图像
    # 显示预测标签，正确的显示为黑色，错误的显示为红色
    color = 'black' if yfit[i] == ytest[i] else 'red'
    axi.set_title(faces.target_names[yfit[i]], color=color)
    axi.set(xticks=[], yticks=[])  # 去除坐标轴

from sklearn.metrics import classification_report

# 6）打印分类报告，包括准确率、召回率和F1分数等指标
print("Classification Report:")
print(classification_report(ytest, yfit, target_names=faces.target_names))

from sklearn.metrics import confusion_matrix
import seaborn as sns

# 7）计算混淆矩阵，并绘制热力图，横轴为真实标签，纵轴为预测标签
mat = confusion_matrix(ytest, yfit)  # 计算混淆矩阵
plt.figure(figsize=(10, 8))  # 设置图形大小
sns.heatmap(mat, annot=True, fmt="d", cmap="Blues", xticklabels=faces.target_names,
            yticklabels=faces.target_names)  # 使用热力图显示
plt.xlabel("Predicted Labels")  # 设置x轴标签
plt.ylabel("True Labels")  # 设置y轴标签
plt.title("Confusion Matrix")  # 设置图形标题
plt.show()  # 显示图形