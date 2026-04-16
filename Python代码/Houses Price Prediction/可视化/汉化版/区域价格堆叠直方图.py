import pandas as pd
import matplotlib.pyplot as plt

# 设置中文字体（Mac 推荐使用苹方或宋体）
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS']  # 或者 'STSong' 'PingFang SC'
plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题

# 1. 读取数据
df = pd.read_csv(r'/Users/jia/Desktop/学习 /论文/数据/数据处理/北京二手房成交_1.6.csv')

# 2. 定义价格分段函数（中文标签）
def price_category(price):
    if price > 800:
        return '大于800万'
    elif 600 < price <= 800:
        return '600~800万'
    elif 400 < price <= 600:
        return '400~600万'
    elif 200 < price <= 400:
        return '200~400万'
    else:
        return '小于200万'

# 3. 应用价格分类
df['价格区间'] = df['价格'].apply(price_category)

# 4. 区域保持中文，不做替换
# （此处省略替换区域名的代码）

# 5. 统计每个区域、每个价格段的数量
grouped = df.groupby(['区域', '价格区间']).size().unstack(fill_value=0)

# 6. 保证列顺序（中文顺序）
price_levels = ['大于800万', '600~800万', '400~600万', '200~400万', '小于200万']
grouped = grouped[price_levels]

# 7. 排序区域（按样本总数从高到低）
grouped['总数'] = grouped.sum(axis=1)
grouped = grouped.sort_values(by='总数', ascending=False).drop(columns='总数')

# 8. 指定颜色
colors = ['#CF3D3E', '#F46F43', '#FBDD85', '#80A6E2', '#403990']

# 9. 绘制堆叠柱状图（含边框线）
ax = grouped.plot(kind='bar', stacked=True, color=colors, figsize=(14, 7), edgecolor='black')

# 10. 添加柱状图顶部标签（总数）
totals = grouped.sum(axis=1)
for i, total in enumerate(totals):
    ax.text(i, total + 2, str(total), ha='center', va='bottom', fontsize=10)

# 11. 美化图形（全部中文）
plt.title('北京各区域二手房价格分布', fontsize=20, fontweight='bold')
plt.xlabel('区域', fontsize=16, fontweight='bold')
plt.ylabel('成交套数', fontsize=16, fontweight='bold')
plt.legend(title='价格区间（万元）', fontsize=10, title_fontsize=11)
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.grid(axis='y', linestyle='--', alpha=0.5)

# 12. 显示图形
plt.show()
