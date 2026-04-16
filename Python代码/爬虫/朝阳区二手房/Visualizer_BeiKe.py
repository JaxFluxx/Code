import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import os

# 设置Matplotlib使用中文字体
plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号

# 读取Excel文件
file_path = r"C:\Users\何嘉\Desktop\朝阳二手房贝壳\朝阳二手房数据_贝壳网_清洗后.test.xlsx"
df = pd.read_excel(file_path)

# 确保数据正确读取
print(df.head())

# 数据清洗：去除可能的空值
df.dropna(inplace=True)

# 基础统计分析
print("\n基础统计信息：")
print(df.describe())

# 区域房价比较
region_price_comparison = df.groupby('区域')['价格(万元)'].mean().sort_values()
print("\n区域房价比较：")
print(region_price_comparison)

# 过滤掉字符中的空格
region_price_comparison.index = region_price_comparison.index.str.replace(r'\s+', '')

plt.figure(figsize=(20, 10))
ax = sns.barplot(x=region_price_comparison.index, y=region_price_comparison.values)
plt.xticks(rotation=45)
plt.title('区域房价比较')
plt.xlabel('区域')
plt.ylabel('平均价格（万元）')

# 添加y轴坐标标签
for p in ax.patches:
    ax.text(p.get_x() + p.get_width() / 2., p.get_height(), f'{p.get_height():.2f}',
            fontsize=10, color='black', ha='center', va='bottom', rotation=60)

plt.show()

# 房价饼状图
price_ranges = [
    (200, 400),
    (450, 800),
    (800, float('inf'))
]

labels = ['200-400万元', '450-800万元', '800万元以上']
sizes = []

for low, high in price_ranges:
    count = df[(df['价格(万元)'] >= low) & (df['价格(万元)'] < high)].shape[0]
    sizes.append(count)

plt.figure(figsize=(8, 8))
plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140)
plt.title('房价区间分布')
plt.show()

# 房价分布
plt.figure(figsize=(10, 6))
ax = sns.histplot(df['价格(万元)'], bins=30, kde=True)
plt.title('房价分布')
plt.xlabel('价格（万元）')
plt.ylabel('密度')

plt.show()

# 显示出单价的分布情况
plt.figure(figsize=(10, 6))
ax = sns.histplot(df['单价(元/平米)'], bins=30, kde=True)
plt.title('单价分布(元/平米)')
plt.xlabel('单价（元/平米）')
plt.ylabel('密度')

plt.show()

# 建成年代对单价的影响
# 筛选1960年到2024年之间的数据
df_filtered = df[(df['建成年代'] >= 1960) & (df['建成年代'] <= 2024)]

built_year_effect = df_filtered.sort_values(by=['建成年代', '单价(元/平米)'], ascending=[True, False])
print("\n建成年代对单价的影响：")
print(built_year_effect[['建成年代', '单价(元/平米)']].head())

plt.figure(figsize=(12, 6))
sns.scatterplot(x='建成年代', y='单价(元/平米)', data=df_filtered, alpha=0.3, color='darkblue')
plt.title('建成年代对单价的影响')
plt.xlabel('建成年代')
plt.ylabel('单价（元/平米）')
plt.show()

# 以年代为x轴，y轴是建成年代对单价的程度
plt.figure(figsize=(12, 6))
sns.lineplot(x='建成年代', y='单价(元/平米)', data=df_filtered, color='darkblue')
plt.title('建成年代对单价的影响程度')
plt.xlabel('建成年代')
plt.ylabel('单价影响程度（元/平米）')
plt.show()

# 拟合函数
years = df['建成年代'].values
prices_per_sqm = df['单价(元/平米)'].values
slope, intercept, r_value, p_value, std_err = stats.linregress(years, prices_per_sqm)
print(f"\n拟合函数: 单价 = {slope:.2f} * 建成年代 + {intercept:.2f}")

# 单价最高和最低的小区
highest_price_neighborhoods = df.nlargest(5, '单价(元/平米)')
lowest_price_neighborhoods = df.nsmallest(3, '单价(元/平米)')

print("\n单价最高的前3个小区：")
print(highest_price_neighborhoods)
print("\n单价最低的前3个小区：")
print(lowest_price_neighborhoods)

plt.figure(figsize=(14, 7))

plt.subplot(1, 2, 1)
ax1 = sns.barplot(x='小区', y='单价(元/平米)', data=highest_price_neighborhoods)
plt.title('单价最高的前3个小区')
plt.xlabel('小区')
plt.ylabel('单价（元/平米）')

# 添加y轴坐标标签
for p in ax1.patches:
    ax1.text(p.get_x() + p.get_width() / 2., p.get_height(), f'{p.get_height():.2f}',
            fontsize=12, color='black', ha='center', va='bottom')

plt.subplot(1, 2, 2)
ax2 = sns.barplot(x='小区', y='单价(元/平米)', data=lowest_price_neighborhoods)
plt.title('单价最低的前3个小区')
plt.xlabel('小区')
plt.ylabel('单价（元/平米）')

# 添加y轴坐标标签
for p in ax2.patches:
    ax2.text(p.get_x() + p.get_width() / 2., p.get_height(), f'{p.get_height():.2f}',
            fontsize=12, color='black', ha='center', va='bottom')

plt.show()

# 检查并创建目录
save_path = r"C:\Users\何嘉\Desktop\可视化数据.txt"
if not os.path.exists(save_path):
    os.makedirs(save_path)

# 将输出保存到txt文件
with open(os.path.join(save_path, 'output.txt'), 'w', encoding='utf-8') as f:
    f.write("确保数据正确读取:\n")
    f.write(df.head().to_string())
    f.write("\n\n基础统计信息:\n")
    f.write(df.describe().to_string())
    f.write("\n\n区域房价比较:\n")
    f.write(region_price_comparison.to_string())
    f.write("\n\n房价区间分布:\n")
    f.write(labels[0] + ": " + str(sizes[0]) + "套\n")
    f.write(labels[1] + ": " + str(sizes[1]) + "套\n")
    f.write(labels[2] + ": " + str(sizes[2]) + "套\n")


print("输出已保存到output.txt文件")
