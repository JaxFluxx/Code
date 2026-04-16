import pandas as pd
import matplotlib.pyplot as plt

plt.rcParams['font.sans-serif'] = ['Arial Unicode MS']
plt.rcParams['axes.unicode_minus']=False #用来正常显示负号

def aggregate_president_heights(file_path):
    # 读取CSV文件
    data = pd.read_csv(file_path, header=None)  # 读取文件，忽略第一行
    data.columns = ['order', 'name', 'height(cm)']  # 根据文件内容设置列名

    # 清洗数据
    data['height(cm)'] = pd.to_numeric(data['height(cm)'], errors='coerce')  # 转换为数值类型，errors='coerce'表示遇到错误时自动填充为NaN
    data = data.dropna(subset=['height(cm)'])  # 去除身高为空的行, subset指定需要检查的列

    # 计算最大值、最小值、平均值和中位数
    max_height = data['height(cm)'].max()
    min_height = data['height(cm)'].min()
    mean_height = data['height(cm)'].mean()
    median_height = data['height(cm)'].median()

    # 打印结果
    print(f"最大身高: {max_height} cm")
    print(f"最小身高: {min_height} cm")
    print(f"平均身高: {mean_height:.2f} cm")
    print(f"中位数身高: {median_height} cm")

    # 绘制直方图
    plt.figure(figsize=(10, 6))  #figsize=(长,宽)
    plt.hist(data['height(cm)'], bins=20, edgecolor='black')    # bins表示直方图的柱数,edgecolor表示边框颜色
    plt.title('美国总统身高分布直方图')
    plt.xlabel('身高（cm）')
    plt.ylabel('总统数量')
    plt.grid(True)
    plt.show()

# 调用数据聚合函数
file_path = 'president_heights.csv'
aggregate_president_heights(file_path)