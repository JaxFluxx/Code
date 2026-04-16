import pandas as pd

# 原文件路径
file_path = '/Users/jia/Desktop/论文/数据/数据处理/北京二手房成交_1.5.csv'

# 读取CSV文件
df = pd.read_csv(file_path)

# 添加 id 列（从1开始递增）
df.insert(0, 'id', range(1, len(df) + 1))

# 覆盖保存到原文件
df.to_csv(file_path, index=False, encoding='utf-8-sig')

print("已在原文件中添加 id 列并覆盖保存：", file_path)
