# 生成圆形数据：
#
# 使用 make_circles 函数生成一个包含1500个点的圆形数据集，并进行标准化处理。
# 肘方法选择最优簇数：
#
# 通过计算不同簇数下的误差平方和(SSE)并绘制折线图，选择最佳的簇数K。
# K-Means聚类：
#
# 使用选择的最优K值进行K-Means聚类，绘制聚类结果的散点图。
# DBSCAN聚类：
#
# 使用DBSCAN算法进行聚类，绘制聚类结果的散点图。
# 轮廓系数比较：
#
# 计算K-Means与DBSCAN的轮廓系数，并绘制柱状图进行比较。

import matplotlib.pyplot as plt
from sklearn.datasets import make_circles
from sklearn.cluster import KMeans, DBSCAN
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler

plt.rcParams['font.sans-serif'] = ['Arial Unicode MS'] #苹果系统显示中文字体

# 1）生成圆形数据并可视化
X, _ = make_circles(n_samples=1500, factor=0.5, noise=0.1, random_state=9)
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

plt.figure(figsize=(8, 6))
plt.scatter(X_scaled[:, 0], X_scaled[:, 1], s=10, color='cyan')
plt.title("原始圆形数据集", fontsize=16)
plt.xlabel("特征1", fontsize=14)
plt.ylabel("特征2", fontsize=14)
plt.axis('equal')
plt.show()

# 2）使用肘方法选择K-Means的最优簇数
sse = []
K = range(1, 11)

for k in K:
    kmeans = KMeans(n_clusters=k, random_state=0)
    kmeans.fit(X_scaled)
    sse.append(kmeans.inertia_)

plt.figure(figsize=(8, 6))
plt.plot(K, sse, marker='o', color='purple')
plt.title("K-Means肘方法", fontsize=16)
plt.xlabel("簇数 (K)", fontsize=14)
plt.ylabel("误差平方和 (SSE)", fontsize=14)
plt.xticks(K)
plt.grid()
plt.show()

# 3）使用K-Means进行聚类并可视化
optimal_k = 2
kmeans = KMeans(n_clusters=optimal_k, random_state=0)
labels_kmeans = kmeans.fit_predict(X_scaled)

plt.figure(figsize=(8, 6))
plt.scatter(X_scaled[:, 0], X_scaled[:, 1], c=labels_kmeans, s=10, cmap='spring')
plt.title("K-Means聚类结果", fontsize=16)
plt.xlabel("特征1", fontsize=14)
plt.ylabel("特征2", fontsize=14)
plt.axis('equal')
plt.show()

# 4）使用DBSCAN聚类算法并可视化
dbscan = DBSCAN(eps=0.2, min_samples=5)
labels_dbscan = dbscan.fit_predict(X_scaled)

plt.figure(figsize=(8, 6))
plt.scatter(X_scaled[:, 0], X_scaled[:, 1], c=labels_dbscan, s=10, cmap='autumn')
plt.title("DBSCAN聚类结果", fontsize=16)
plt.xlabel("特征1", fontsize=14)
plt.ylabel("特征2", fontsize=14)
plt.axis('equal')
plt.show()

# 5）比较K-Means与DBSCAN的轮廓系数
silhouette_kmeans = silhouette_score(X_scaled, labels_kmeans)
silhouette_dbscan = silhouette_score(X_scaled, labels_dbscan)

plt.figure(figsize=(8, 6))
labels = ['K-Means', 'DBSCAN']
scores = [silhouette_kmeans, silhouette_dbscan]
plt.bar(labels, scores, color=['green', 'orange'])
plt.title("K-Means与DBSCAN的轮廓系数比较", fontsize=16)
plt.ylabel("轮廓系数", fontsize=14)
plt.ylim(0, 1)
plt.show()
