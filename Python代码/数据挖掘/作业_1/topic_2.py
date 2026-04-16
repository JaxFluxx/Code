import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

plt.rcParams['font.sans-serif'] = ['Arial Unicode MS']

def handle_missing_values(file_path):
    # 读取CSV文件
    data = pd.read_csv(file_path)

    # 数据检查：打印出哪些列包含缺失值以及每列缺失值的数量
        # 计算每列缺失值的数量,isnull()返回True/False矩阵，sum()返回每列缺失值的数量
    missing_values_count = data.isnull().sum()
    print("列包含缺失值的数量：")
    print(missing_values_count)

    # 绘制缺失值分布图
    plt.figure(figsize=(10, 6))
    sns.barplot(x=missing_values_count.index, y=missing_values_count.values, palette='viridis')
    plt.xticks(rotation=45)
    plt.title('缺失值分布图')
    plt.xlabel('列名')
    plt.ylabel('缺失值数量')
    plt.show()

    # 缺失值处理
    # 对数值类型的列，使用列的平均值填充缺失值
    for column in data.select_dtypes(include=['float64', 'int64']).columns:     # include=['float64', 'int64']筛选出数值类型列
        data[column].fillna(data[column].mean(), inplace=True)  # fillna()用平均值填充缺失值

    # 对字符类型的列，使用“未知”("Unknown")填充缺失值
    for column in data.select_dtypes(include=['object']).columns:
        data[column].fillna("Unknown", inplace=True)

    # 结果展示：输出清洗后的数据
    print("处理后的数据前20行：")
    print(data.head(20))

    # 返回处理完缺失值后的DataFrame
    return data

# 调用函数处理缺失值
file_path = "/Users/jia/Desktop/学习/数据挖掘/Mzitu/数据挖掘/作业_1/NonValueProcess_data.csv"
df_cleaned = handle_missing_values(file_path)
