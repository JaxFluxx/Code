import pandas as pd
from sklearn.model_selection import train_test_split

# 1. 读取已处理好的数据集
file_path = r'/Users/jia/Desktop/学习 /机器学习/数据/1.4.csv'
df = pd.read_csv(file_path)

# 2. 随机划分，test_size=0.2，随机种子固定保证结果可复现
train_df, test_df = train_test_split(df, test_size=0.2, random_state=42, shuffle=True)

# 3. 保存训练集和测试集
train_path = r'/Users/jia/Desktop/学习 /机器学习/数据/train_1.5.csv'
test_path = r'/Users/jia/Desktop/学习 /机器学习/数据/test_1.5.csv'

train_df.to_csv(train_path, index=False)
test_df.to_csv(test_path, index=False)

print(f"✅ 训练集保存为：{train_path}")
print(f"✅ 测试集保存为：{test_path}")
