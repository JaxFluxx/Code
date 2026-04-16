import pandas as pd
import matplotlib.pyplot as plt

plt.rcParams['font.sans-serif'] = ['Arial Unicode MS']

# 1. 读取数据
df = pd.read_csv(r'/Users/jia/Desktop/学习 /论文/数据/数据处理/北京二手房成交_1.6.csv')

# 2. 定义价格分段函数
def price_category(price):
    if price > 800:
        return 'P>800'
    elif 600 < price <= 800:
        return '600~800'
    elif 400 < price <= 600:
        return '400~600'
    elif 200 < price <= 400:
        return '200~400'
    else:
        return '<200'

# 3. 应用价格分类
df['价格区间'] = df['价格'].apply(price_category)

# 4. 替换区域名为英文
area_name_map = {
    '东城': 'Dongcheng', '西城': 'Xicheng', '海淀': 'Haidian', '朝阳': 'Chaoyang', '丰台': 'Fengtai',
    '石景山': 'Shijingshan', '通州': 'Tongzhou', '大兴': 'Daxing', '昌平': 'Changping', '房山': 'Fangshan',
    '顺义': 'Shunyi', '门头沟': 'Mentougou', '亦庄开发区': 'Yizhuang Development Zone', '怀柔': 'Huairou',
    '密云': 'Miyun', '延庆': 'Yanqing', '平谷': 'Pinggu'
}
df['区域'] = df['区域'].replace(area_name_map)

# 5. 统计每个区域、每个价格段的数量
grouped = df.groupby(['区域', '价格区间']).size().unstack(fill_value=0)

# 6. 保证列顺序（颜色对应）
price_levels = ['P>800', '600~800', '400~600', '200~400', '<200']
grouped = grouped[price_levels]

# 7. 排序区域（按样本总数从高到低）
grouped['总数'] = grouped.sum(axis=1)
grouped = grouped.sort_values(by='总数', ascending=False).drop(columns='总数')

# 8. 使用指定颜色（你提供的五种）
colors = ['#CF3D3E', '#F46F43', '#FBDD85', '#80A6E2', '#403990']


# 9. 绘制堆叠柱状图（含边框线）
ax = grouped.plot(kind='bar', stacked=True, color=colors, figsize=(14, 7), edgecolor='black')

# 10. 添加柱状图顶部标签（总数）
totals = grouped.sum(axis=1)
for i, total in enumerate(totals):
    ax.text(i, total + 2, str(total), ha='center', va='bottom', fontsize=10)

# 11. 美化图形
plt.title('House Price Distribution by Region', fontsize=20, fontweight='bold')
plt.xlabel('Area', fontsize=16,fontweight='bold')
plt.ylabel('Number of Listings', fontsize=16,fontweight='bold')
plt.legend(title='Price Segment\n(×10,000 RMB)', fontsize=10, title_fontsize=11)
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.grid(axis='y', linestyle='--', alpha=0.5)

# 12. 显示图形
plt.show()
