import pandas as pd

# 读取Excel文件
file_path = r'C:\Users\何嘉\Desktop\朝阳二手房数据.xlsx'
df = pd.read_excel(file_path)

# 数据清洗
# 价格为整数，若为负数则取绝对值
df['价格(万元)'] = df['价格(万元)'].apply(lambda x: abs(int(float(x))))

# 只保留面积、单价和年代的数字部分
df['面积(平米)'] = df['面积(平米)'].apply(lambda x: ''.join(filter(lambda i: i.isdigit(), str(x))))
df['单价(元/平米)'] = df['单价(元/平米)'].apply(lambda x: ''.join(filter(lambda i: i.isdigit(), str(x))))
df['建成年代'] = df['建成年代'].apply(lambda x: ''.join(filter(lambda i: i.isdigit(), str(x))))

# # 移除空值
# df.dropna(inplace=True)

# 去除重复数据
df.drop_duplicates(inplace=True)

# 将异常数据修改到合理值
df['价格(万元)'] = df['价格(万元)'].apply(lambda x: max(10, min(x, 100000000)))
df['面积(平米)'] = df['面积(平米)'].apply(lambda x: max(10, min(int(x), 50000000)))
df['单价(元/平米)'] = df['单价(元/平米)'].apply(lambda x: max(1000, min(int(x), 200000000)))

# 保存清洗后的数据到新的Excel文件
cleaned_file_path = r'C:\Users\何嘉\Desktop\朝阳二手房数据_清洗后.xlsx'
df.to_excel(cleaned_file_path, index=False)

print("数据清洗完成，并已保存到新文件。")