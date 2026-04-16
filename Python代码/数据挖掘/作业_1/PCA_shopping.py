# 导入必要的库
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from mpl_toolkits.mplot3d import Axes3D  # 导入3D绘图工具

plt.rcParams['font.sans-serif'] = ['Arial Unicode MS']


# 编写执行PCA分析的函数
def perform_pca(file_path):
    data = pd.read_csv(file_path)

    # 标准化数据
    scaler = StandardScaler()
    data_scaled = scaler.fit_transform(data)

    # 使用散点图矩阵查看特征之间的关系
    sns.pairplot(data)
    plt.suptitle('原始数据的散点图矩阵')
    plt.show()


    # 降维到2维
    pca_2d = PCA(n_components=2)
    pca_2d.fit(data_scaled)
    X_pca2 = pca_2d.transform(data_scaled)  # transform数据到新空间

    # 绘制PCA结果
    plt.figure(figsize=(8, 6))
    plt.scatter(X_pca2[:, 0], X_pca2[:, 1], c='r', marker='o')
    plt.xlabel('PC1')
    plt.ylabel('PC2')
    plt.title('PCA Result')
    plt.axis('equal')
    plt.show()

    # 降维到3维
    pca_3d = PCA(n_components=3)
    pca_3d.fit(data_scaled)
    X_pca3 = pca_3d.transform(data_scaled)  # transform数据到新空间

    # 绘制PCA结果3D
    # 绘制PCA结果（3个主成分）
    fig = plt.figure(figsize=(8, 6))
    ax = fig.add_subplot(111, projection='3d')
    ax.scatter(X_pca3[:, 0], X_pca3[:, 1], X_pca3[:, 2], c='b', marker='o')
    ax.set_xlabel('PC1')
    ax.set_ylabel('PC2')
    ax.set_zlabel('PC3')
    plt.title('PCA Result with 3 Components')
    # 设置观察角度
    ax.view_init(elev=30, azim=60)
    plt.show()

    # 绘制累计解释方差比例图，展示主成分分析（PCA）中各个主成分对数据方差的解释能力
    plt.figure(figsize=(8, 6))
    # 计算累计方差
    cumulative_variance = pca_3d.explained_variance_ratio_.cumsum() # cumsum() 函数计算这些比例的累积和，结果表示随着主成分数量的增加，总的解释方差的比例

    # 绘图
    plt.plot(cumulative_variance, marker= 'o')
    plt.xlabel('主成分数量')
    plt.ylabel('主成分累计解释方差')
    plt.title('累积解释方差比率图')
    # 花两条参考线
    plt.axhline(y=0.9, color='r', linestyle='--')
    plt.axhline(y=0.8, color='g', linestyle='--')

    plt.grid(True)
    plt.show()


# 调用函数并进行PCA分析
file_path = "./shopping_data.csv"
perform_pca(file_path)