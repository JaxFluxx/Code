import pandas as pd

# 读取原始数据
df = pd.read_csv('/Users/jia/Desktop/论文/数据/数据处理/北京二手房成交_1.6.csv')

# 为商圈列中的唯一值按出现顺序编码
unique_values = []
encoding = {}
codes = []

for item in df['商圈']:
    if item not in encoding:
        encoding[item] = len(encoding)
        unique_values.append(item)
    codes.append(encoding[item])

# 添加编码列到原始数据（可选）
df['商圈编码'] = codes

# 保存编码对应关系为CSV
encoding_df = pd.DataFrame({
    '商圈': unique_values,
    '编码': list(range(len(unique_values)))
})
encoding_df.to_csv('/Users/jia/Desktop/论文/数据/数据处理/北京二手房成交_1.7.0_商圈映射表.csv', index=False)

# 如果你还想保存加上编码列的完整数据表，也可以加下面这行
# df.to_csv('带编码的原始数据.csv', index=False)

print("编码完成，对应关系表已保存为 '/Users/jia/Desktop/论文/数据/数据处理/北京二手房成交_1.7.0.csv'")
