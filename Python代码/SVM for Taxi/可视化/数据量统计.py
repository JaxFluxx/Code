import pandas as pd

# 读取CSV文件
file_path = '/Users/jia/Desktop/学习 /机器学习/数据/1.3.csv'
df = pd.read_csv(file_path)

# 打印总行数（即数据条数）
print(f"总数据条数：{len(df)}")
