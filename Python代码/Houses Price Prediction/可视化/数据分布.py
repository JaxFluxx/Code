import pandas as pd

# 读取CSV文件（替换为你的文件路径）
file_path = r'/Users/jia/Desktop/论文/数据/数据处理/北京二手房成交_1.5.csv'  # 比如 'data.csv'
df = pd.read_csv(file_path)

# 遍历每一列，统计每个值的频率
for column in df.columns:
    print(f"\n列：{column}")
    print(df[column].value_counts(dropna=False))  # dropna=False 保留 NaN 的计数

# 找出最低价格
min_price = df['价格'].min()
print(f"\n最低价格：{min_price}")

