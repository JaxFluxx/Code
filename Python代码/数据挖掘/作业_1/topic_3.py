import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

plt.rcParams['font.sans-serif'] = ['Arial Unicode MS']

def birth_data_pivot_table(file_path):
    # 读取CSV文件
    data = pd.read_csv(file_path)

    # 1) 使用 Year 作为行索引，计算每年的出生人口总和
    total_births_per_year = data.groupby('Year')['Births'].sum().reset_index()  #reset_index()用于重置索引
    print("每年的出生人口总和：")
    print(total_births_per_year)

    # 2) 使用 Month 作为列索引，创建数据透视表
    pivot_table_month = pd.pivot_table(data, values='Births', index='Year', columns='Month', aggfunc='sum', margins=True)
    print("使用 Month 作为列索引的数据透视表：")
    print(pivot_table_month)

    # 3) 对 Births 列进行聚合，计算每个年份在每个月的出生人数总和，并绘制热力图
    pivot_table_year = pd.pivot_table(data, values='Births', index='Year', columns='Month', aggfunc='sum')

    plt.figure(figsize=(12, 8))
    sns.heatmap(pivot_table_year, annot=True, fmt="d", cmap='coolwarm')
    plt.title('每年每月的出生人数总和热力图')
    plt.xlabel('Month')
    plt.ylabel('Year')
    plt.show()

    # 4) 通过 Gender 进行分组，分别统计男性和女性的出生人数，并绘制折线图
    # 首先对数据进行分组与汇总
    grouped_data = data.groupby(['Year', 'Gender'])['Births'].sum().reset_index()

    # 绘制男性和女性出生趋势折线图
    plt.figure(figsize=(12, 6))
    sns.lineplot(data=grouped_data, x='Year', y='Births', hue='Gender', marker='o')
    plt.title('男性和女性的出生趋势折线图')
    plt.xlabel('Year')
    plt.ylabel('出生人数')
    plt.legend(title='Gender')
    plt.show()


# 调用函数进行数据分析
file_path = 'births.csv'
birth_data_pivot_table(file_path)