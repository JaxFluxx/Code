import pandas as pd

# 设置文件路径
input_path = '/Users/jia/Desktop/论文/数据/数据处理/北京二手房成交_1.7.2.csv'
output_cleaned_path = '/Users/jia/Desktop/论文/数据/数据处理/北京二手房成交_1.7.3.csv'


# 读取CSV文件
df = pd.read_csv(input_path)

# 剔除所有包含空值的行
df_clean = df.dropna()

# 保存清洗后的数据
df_clean.to_csv(output_cleaned_path, index=False, encoding='utf-8-sig')

print("清洗后的文件已保存：", output_cleaned_path)
