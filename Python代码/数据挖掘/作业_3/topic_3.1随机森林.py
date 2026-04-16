# 步骤1：生成数据集并绘制散点图，根据类别对点进行上色。
# 步骤2：初始化决策树分类器，对数据进行分类，并可视化分类效果。
# 步骤3：通过袋装方法组合多个决策树分类器，提高模型的分类性能，并可视化分类效果。
# 步骤4：使用随机森林模型（即多个决策树的组合）进行分类，并可视化分类效果。


# lab3_3_1
import numpy as np
import matplotlib.pyplot as plt
from sklearn.datasets import make_blobs

plt.rcParams['font.sans-serif'] = ['Arial Unicode MS']  # 苹果系统显示中文字体

# 1）生成数据集并绘制散点图
X, y = make_blobs(n_samples=300, centers=4, random_state=0, cluster_std=1.0)  #使用make_blobs生成300个样本点，分成4个簇
plt.scatter(X[:, 0], X[:, 1], c=y, s=30, cmap='rainbow')  # 彩虹配色
plt.title("Scatter plot of generated blobs")
plt.show()


# 定义可视化函数 visualize_classifier，用于展示分类器效果
def visualize_classifier(model, X, y, ax=None, cmap='rainbow'):
    ax = ax or plt.gca()

    # 绘制训练点
    ax.scatter(X[:, 0], X[:, 1], c=y, s=30, cmap=cmap,
               clim=(y.min(), y.max()), zorder=3)  #绘制数据点，上色
    ax.axis('tight')  #自动调整坐标轴的范围
    ax.axis('off')  #隐藏坐标轴
    xlim = ax.get_xlim()
    ylim = ax.get_ylim()

    # 训练分类模型
    model.fit(X, y)  # 训练模型
    xx, yy = np.meshgrid(np.linspace(*xlim, num=200),
                         np.linspace(*ylim, num=200))
    Z = model.predict(np.c_[xx.ravel(), yy.ravel()]).reshape(xx.shape)  #对网格点进行预测并重塑为图形大小

    # 使用预测结果创建颜色填充图
    n_classes = len(np.unique(y))  # 获取类别数
    contours = ax.contourf(xx, yy, Z, alpha=0.3,
                           levels=np.arange(n_classes + 1) - 0.5,
                           cmap=cmap, zorder=1)  #绘制分类边界

    ax.set(xlim=xlim, ylim=ylim)  #坐标轴范围


from sklearn.tree import DecisionTreeClassifier

# 2）初始化决策树分类器并训练模型，使用 visualize_classifier 进行可视化
tree_model = DecisionTreeClassifier(random_state=0)  #初始化决策树分类器
visualize_classifier(tree_model, X, y)  #visualize_classifier函数进行分类效果可视化
plt.title("Decision Tree Classifier")
plt.show()  # 显示图形

from sklearn.ensemble import BaggingClassifier

# 3）使用袋装方法结合多个决策树分类器，增强分类性能，并可视化
bag_model = BaggingClassifier(base_estimator=DecisionTreeClassifier(),  # 使用决策树作为基础分类器
                              n_estimators=100,  #100棵树
                              max_samples=0.8,  #每棵树使用80%的样本
                              random_state=0)  #随机种子
visualize_classifier(bag_model, X, y)
plt.title("Bagging with Decision Trees")
plt.show()

from sklearn.ensemble import RandomForestClassifier

# 4）使用随机森林模型进行分类，并可视化
forest_model = RandomForestClassifier(n_estimators=100, random_state=0)  #初始化随机森林分类器，100棵树
visualize_classifier(forest_model, X, y)  #可视化
plt.title("Random Forest Classifier")
plt.show()  # 显示图形
