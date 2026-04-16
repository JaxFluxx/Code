import pandas as pd
from sklearn.preprocessing import StandardScaler

# 读取清理后的CSV文件
df = pd.read_csv('/Users/jia/Desktop/论文/数据/数据处理/北京二手房成交_1.7.3.csv')

# 提取数值型特征列（去掉 'id' 列和非数值列）
numeric_columns = df.select_dtypes(include=['float64', 'int64']).columns
numeric_columns = [col for col in numeric_columns if col != 'id']  # 排除 'id' 列

# 初始化 StandardScaler 对象
scaler = StandardScaler()

# 对数值数据进行标准化
df[numeric_columns] = scaler.fit_transform(df[numeric_columns])

# 打印关键数据（均值和标准差）
for i, col in enumerate(numeric_columns):
    print(f"列名: {col}")
    print(f"均值: {scaler.mean_[i]}")
    print(f"标准差: {scaler.scale_[i]}")
    print("-" * 20)

# 保存归一化后的数据到新的CSV文件
df.to_csv('/Users/jia/Desktop/论文/数据/数据处理/北京二手房成交_1.8.csv', index=False)

print("数据已归一化并保存")
