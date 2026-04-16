import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA

'''
在这段代码中：

pca.fit(X) 负责对原始空间的数据进行分析，计算出主成分。
X_pca = pca.transform(X) 将原始数据转换到主成分空间。
X_new = pca.inverse_transform(X_pca) 将降维后的数据尽可能地重构回原始空间，以便于比较原始数据和重构数据的相似度。
通过这种方式，PCA能够减少特征数量，同时保留最重要的信息，从而为后续的数据分析或可视化打下基础。
'''


# 生成数据
rng = np.random.RandomState(1)  # 设置随机种子
X = np.dot(rng.rand(2, 2), rng.randn(2, 200)).T # 生成200个样本，每个样本有2个特征

# 初始化PCA对象并进行拟合
pca = PCA(n_components=1)
pca.fit(X)
X_pca = pca.transform(X)    #将原始数据X转换为主成分空间，得到降维后的数据。
print("original shape:   ", X.shape)
print("transformed shape:", X_pca.shape)

X_new = pca.inverse_transform(X_pca)    #将降维后的数据转换回原始空间，得到重构数据。
plt.scatter(X[:, 0], X[:, 1], alpha=0.2)
plt.scatter(X_new[:, 0], X_new[:, 1], alpha=0.8)
plt.axis('equal')
plt.show()