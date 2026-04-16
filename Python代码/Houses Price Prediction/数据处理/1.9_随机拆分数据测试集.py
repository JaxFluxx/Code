import pandas as pd
from sklearn.model_selection import train_test_split

# 原始文件路径
file_path = '/Users/jia/Desktop/论文/数据/数据处理/北京二手房成交_1.8.csv'

# 读取数据
df = pd.read_csv(file_path)

# 拆分数据：80% 训练集，20% 测试集
train_df, test_df = train_test_split(df, test_size=0.2, random_state=42)

# 保存到两个新文件中
train_path = '/Users/jia/Desktop/论文/数据/数据处理/北京二手房成交_1.9_train.csv'
test_path = '/Users/jia/Desktop/论文/数据/数据处理/北京二手房成交_1.9_test.csv'

train_df.to_csv(train_path, index=False, encoding='utf-8-sig')
test_df.to_csv(test_path, index=False, encoding='utf-8-sig')

print("训练集已保存：", train_path)
print("测试集已保存：", test_path)
