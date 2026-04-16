# 导入所需的库
import matplotlib.pyplot as plt
import numpy as np
from sklearn.datasets import make_blobs
from sklearn.cluster import KMeans

# 数据集，包含300个样本，4个中心
X, y_true = make_blobs(n_samples=300, centers=4,
                       cluster_std=0.60, random_state=0)

# 1）绘制原始数据散点图，设置点的大小为30
plt.figure(figsize=(8, 6))
plt.scatter(X[:, 0], X[:, 1], s=30, color='cyan')  # 青色
plt.title('原始数据散点图')
plt.xlabel('特征 1')
plt.ylabel('特征 2')
plt.grid()
plt.show()

# 2）使用KMeans进行聚类，设置划分成 4 个簇
kmeans = KMeans(n_clusters=4, random_state=0)  # 创建KMeans对象
y_kmeans = kmeans.fit_predict(X)  # 训练模型并预测每个点的簇标签

# 3）绘制KMeans聚类结果，使用viridis颜色映射表
plt.figure(figsize=(8, 6))
plt.scatter(X[:, 0], X[:, 1], c=y_kmeans, s=30, cmap='spring')  # 修改颜色映射表为spring
centers = kmeans.cluster_centers_  # 获取每个簇的中心
plt.scatter(centers[:, 0], centers[:, 1], c='black', s=100, alpha=0.75, label='簇中心')  # 绘制簇中心
plt.title('KMeans 聚类结果')
plt.xlabel('特征 1')
plt.ylabel('特征 2')
plt.legend()
plt.grid()
plt.show()

# 4）自定义函数实现KMeans聚类
def find_clusters(X, n_clusters=4, rseed=0):
    kmeans = KMeans(n_clusters=n_clusters, random_state=rseed)
    y_kmeans = kmeans.fit_predict(X)  # 训练模型并预测每个点的簇标签
    return kmeans.cluster_centers_, y_kmeans  # 返回簇中心和标签

# 使用自定义函数进行聚类
centers_custom, labels_custom = find_clusters(X, n_clusters=4)

# 可视化自定义函数的聚类结果
plt.figure(figsize=(8, 6))
plt.scatter(X[:, 0], X[:, 1], c=labels_custom, s=30, cmap='spring')  # 修改颜色映射表为spring
plt.scatter(centers_custom[:, 0], centers_custom[:, 1], c='black', s=100, alpha=0.75, label='簇中心')
plt.title('自定义 KMeans 聚类结果（簇数=4）')
plt.xlabel('特征 1')
plt.ylabel('特征 2')
plt.legend()
plt.grid()
plt.show()

# 5）设置 rseed=0 重新运行 find_clusters
centers_custom_rseed_0, labels_custom_rseed_0 = find_clusters(X, n_clusters=4, rseed=0)

# 可视化使用 rseed=0 的聚类结果
plt.figure(figsize=(8, 6))
plt.scatter(X[:, 0], X[:, 1], c=labels_custom_rseed_0, s=30, cmap='spring')  # 修改颜色映射表为spring
plt.scatter(centers_custom_rseed_0[:, 0], centers_custom_rseed_0[:, 1], c='black', s=100, alpha=0.75, label='簇中心')
plt.title('自定义 KMeans 聚类结果（rseed=0，簇数=4）')
plt.xlabel('特征 1')
plt.ylabel('特征 2')
plt.legend()
plt.grid()
plt.show()

# 6）将 KMeans 聚类的簇数改为 7，再次对数据进行聚类并绘图
kmeans_7 = KMeans(n_clusters=7, random_state=0)  # 簇数为7
y_kmeans_7 = kmeans_7.fit_predict(X)  # 训练模型并预测每个点的簇标签

# 绘制 KMeans 聚类结果，簇数为7
plt.figure(figsize=(8, 6))
plt.scatter(X[:, 0], X[:, 1], c=y_kmeans_7, s=30, cmap='spring')  # 修改颜色映射表为spring
centers_7 = kmeans_7.cluster_centers_  # 得到每个簇的中心
plt.scatter(centers_7[:, 0], centers_7[:, 1], c='black', s=100, alpha=0.75, label='簇中心')
plt.title('KMeans 聚类结果（簇数=7）')
plt.xlabel('特征 1')
plt.ylabel('特征 2')
plt.legend()
plt.grid()
plt.show()
