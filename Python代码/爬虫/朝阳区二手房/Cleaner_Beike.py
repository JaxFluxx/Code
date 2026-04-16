import pandas as pd

# 读取Excel文件
df = pd.read_excel(r"C:\Users\何嘉\Desktop\朝阳二手房贝壳\朝阳二手房数据_贝壳网_原始.test.xlsx")

# 将空值替换为None
df = df.replace('', None)

# 去除有空值的行
df.dropna(inplace=True)

# 删除重复的行
df.drop_duplicates(inplace=True)

# 处理建成年代数据
def process_years(years):
    if '-' in years:
        start_year, end_year = map(int, years.replace('年', '').split('-'))
        average_year = (start_year + end_year) // 2
        return average_year
    else:
        return int(years.replace('年', ''))

df['建成年代'] = df['建成年代'].apply(process_years)

# 对价格和单价取绝对值
df['价格(万元)'] = df['价格(万元)'].apply(abs)
df['单价(元/平米)'] = df['单价(元/平米)'].apply(abs)

# 保存清洗后的数据到新的Excel文件
df.to_excel(r"C:\Users\何嘉\Desktop\朝阳二手房贝壳\朝阳二手房数据_贝壳网_清洗后.test.xlsx", index=False)

print('清洗完成！')
