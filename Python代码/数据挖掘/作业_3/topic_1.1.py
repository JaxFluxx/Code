# Lab3_1_1
# 把#pass替换为你自己的代码

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns; sns.set()
from sklearn.datasets import make_blobs
from sklearn.naive_bayes import GaussianNB

plt.rcParams['font.sans-serif'] = ['Arial Unicode MS'] #苹果系统显示中文字体

X, y = make_blobs(100, 2, centers=2, random_state=2, cluster_std=1.5)    #生成数据集

# 1）绘制生成的数据点
plt.scatter(X[:, 0], X[:, 1], c=y, cmap='RdBu', s=50)
plt.title("生成的数据点")
plt.xlabel("特征1")
plt.ylabel("特征2")
plt.show()

# 2）初始化并训练GaussianNB模型
模型 = GaussianNB()   # 创建贝叶斯算法实例
模型.fit(X, y)    # 生成的数据集拿来训练模型

# 3）生成新的数据点
伪随机数生成器 = np.random.RandomState(0)
Xnew = 伪随机数生成器.uniform([-6, -14], [8, 4], size=(2000, 2))   # 生成2000个随机数据点

# 4）使用训练好的模型对新生成的数据Xnew进行预测
ynew = 模型.predict(Xnew)

# 绘制原始数据集的散点图
plt.scatter(X[:, 0], X[:, 1], c=y, cmap='RdBu', s=50, label='原始数据')     #散点图绘制
plt.title("原始数据与预测数据")
plt.xlabel("特征1")
plt.ylabel("特征2")

# 绘制预测的新数据点，设置透明度alpha=0.1
plt.scatter(Xnew[:, 0], Xnew[:, 1], c=ynew, cmap='RdBu', s=20, alpha=0.1, label='预测数据')
lim = plt.axis()  # 确保新图和原图有相同的轴范围
plt.legend()
plt.show()

# 5）计算每个新数据点属于每个类别的概率，并输出最后8个点的概率
概率 = 模型.predict_proba(Xnew)     #算出新数据点属于每个类别的概率
print("最后8个新数据点的概率：\n", np.round(概率[-8:], 2))