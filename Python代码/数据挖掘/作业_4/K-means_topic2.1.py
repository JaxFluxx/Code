# 数据生成：
#
# 使用 make_moons 生成一个“月牙形”数据集，包含200个点，并加入噪声以增加复杂度。
# KMeans聚类：
#
# 定义 KMeans 模型，将数据聚类成2个簇。
# fit_predict 方法用于拟合数据并返回每个样本的聚类标签。
# 使用 scatter 方法绘制散点图，设置点的大小为50，使用 viridis 颜色映射表，区分不同的聚类。
# 谱聚类：
#
# 定义 SpectralClustering 模型，设置聚类数量为2，使用最近邻方法计算相似性矩阵，最后通过KMeans进行标签分配。
# 使用 fit_predict 方法拟合数据并返回聚类标签。
# 同样使用 scatter 方法绘制散点图以展示聚类结果。




from sklearn.datasets import make_moons
from sklearn.cluster import KMeans, SpectralClustering
import matplotlib.pyplot as plt

plt.rcParams['font.sans-serif'] = ['Arial Unicode MS'] #苹果系统显示中文字体

# 生成一个由200个点组成的“月牙形”数据集，带有一定的噪声
X, y = make_moons(200, noise=.05, random_state=0)

# 1）使用KMeans算法进行聚类
kmeans = KMeans(n_clusters=2, random_state=0)  # 定义KMeans模型，设置聚类中心为2
labels = kmeans.fit_predict(X)  # 拟合数据并返回聚类标签

# 根据KMeans的聚类结果绘制散点图
plt.figure(figsize=(12, 6))
plt.subplot(1, 2, 1)  # 1行2列，第1个位置
plt.scatter(X[:, 0], X[:, 1], c=labels, s=50, cmap='plasma')
plt.title("KMeans聚类结果", fontsize=16)
plt.xlabel("特征1", fontsize=14)
plt.ylabel("特征2", fontsize=14)
plt.axis('equal')  # 设置坐标轴比例相等

# 2）使用谱聚类进行聚类
spectral_clustering = SpectralClustering(n_clusters=2, affinity='nearest_neighbors', assign_labels='kmeans', random_state=0)
spectral_labels = spectral_clustering.fit_predict(X)  # 拟合数据并返回聚类标签

# 根据谱聚类的结果绘制散点图
plt.subplot(1, 2, 2)  # 1行2列，第2个位置
plt.scatter(X[:, 0], X[:, 1], c=spectral_labels, s=50, cmap='magma')
plt.title("谱聚类结果", fontsize=16)
plt.xlabel("特征1", fontsize=14)
plt.ylabel("特征2", fontsize=14)
plt.axis('equal')  # 设置坐标轴比例相等

plt.tight_layout()
plt.show()
