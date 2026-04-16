import pandas as pd

# 方法1：使用原始字符串 r''，可以防止转义出错
file_path = r'/Users/jia/Desktop/学习 /机器学习/数据/1.1_删除列后.csv'
df = pd.read_csv(file_path)


# 2. 计算每一列的缺失值比例（空或NaN）
missing_ratio = df.isna().mean().reset_index()
missing_ratio.columns = ['Column', 'Missing Ratio']

print("每一列的缺失值比例（表格）：")
print(missing_ratio.to_string(index=False))

# 3. 计算所有“包含缺失值的行”的比例
row_missing_ratio = df.isna().any(axis=1).mean()
print(f"\n含有缺失值的行占总行数的比例：{row_missing_ratio:.2%}")

# 4. 删除所有含缺失值的行
df_cleaned = df.dropna()

# 5. 保存为新的 CSV 文件
df_cleaned.to_csv('/Users/jia/Desktop/学习 /机器学习/数据/1.2.csv', index=False)
print("\n已保存删除缺失行后的文件：cleaned_data.csv")
