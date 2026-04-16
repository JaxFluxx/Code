import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
rng = np.random.RandomState(1)  # 设置随机种子
X = np.dot(rng.rand(2, 2), rng.randn(2, 200)).T # 生成200个样本，每个样本有2个特征
plt.scatter(X[:, 0], X[:, 1])   # 画出原始数据点
plt.axis('equal')
plt.show()


from sklearn.decomposition import PCA
pca = PCA(n_components=2)   # 降维到2维
pca.fit(X)  #DiffCopyInsert这行代码通过调用fit方法来拟合数据集X，计算出数据的主成分。这一步完成后，PCA已经提取出最重要的两个主成分
print(pca.explained_variance_ratio_)    # 输出各主成分的方差比例

def draw_vector(v0, v1, ax=None):
    ax = ax or plt.gca()    # 若ax为空，则默认使用当前坐标系
    arrowprops=dict(arrowstyle='->',
                    linewidth=2,
                    shrinkA=0, shrinkB=0)
    ax.annotate('', v1, v0, arrowprops=arrowprops)  #v0和v1分别是箭头的起点和终点。

# 画图
plt.scatter(X[:, 0], X[:, 1], alpha=0.2)    #这里使用plt.scatter函数绘制原始数据点，X[:, 0]和X[:, 1]分别代表数据的第一列和第二列，alpha=0.2用于设置点的透明度
# 画出主成分的方向
for length, vector in zip(pca.explained_variance_, pca.components_):    #zip(pca.explained_variance_, pca.components_)：将两个列表打包在一起，分别是主成分的方差和对应的主成分向量。
    v = vector * 3 * np.sqrt(length)
    draw_vector(pca.mean_, pca.mean_ + v)
plt.axis('equal')
plt.show()