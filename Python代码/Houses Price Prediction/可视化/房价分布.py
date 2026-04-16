import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import make_interp_spline

# 1. 读取 CSV 文件
df = pd.read_csv(r'/Users/jia/Desktop/学习 /论文/数据/数据处理/北京二手房成交_1.7.3.csv', encoding='utf-8')

# 2. 设置直方图的分组（每50为一个bin）
bin_edges = list(range(0, 2501, 50))
counts, edges = np.histogram(df['价格'], bins=bin_edges)

# 3. 计算bin中心点
bin_centers = 0.5 * (edges[:-1] + edges[1:])

# 4. 对频数进行滑动平均（窗口=3）
window = 3
weights = np.ones(window) / window
counts_smooth = np.convolve(counts, weights, mode='same')

# 5. 创建更平滑的插值曲线（五阶样条 + 高密度点）
x_smooth = np.linspace(bin_centers.min(), bin_centers.max(), 1000)
spline = make_interp_spline(bin_centers, counts_smooth, k=3)
y_smooth = spline(x_smooth)

# 6. 绘制直方图（边框统一粗细 linewidth=1）
plt.figure(figsize=(10, 6))
plt.hist(df['价格'], bins=bin_edges, color='#003366', edgecolor='black', linewidth=1, alpha=0.7, label='Histogram')  # 墨蓝色

# 7. 绘制平滑曲线
plt.plot(x_smooth, y_smooth, color='#800020', linewidth=3, label='Smoothed Curve',)  # 酒红色


# 8. 设置x轴范围与刻度标签（添加 34）
plt.xlim(0, 2500)
xtick_values = np.arange(200, 2501, 200).tolist()

# 添加 34 到刻度值中
xtick_values.append(34)
xtick_values = sorted(xtick_values)

# 构造标签
xtick_labels = [str(x) for x in xtick_values]

# 替换特定标签
if '34' in xtick_labels:
    xtick_labels[xtick_labels.index('34')] = '34\n(min)'
if '2200' in xtick_labels:
    xtick_labels[xtick_labels.index('2200')] = '... ...'
if '2400' in xtick_labels:
    xtick_labels[xtick_labels.index('2400')] = '3800\n(max)'

# 获取当前 tick 对象
tick_objs = plt.xticks(ticks=xtick_values)[1]

# 设置每个 tick 的样式
for label, text in zip(xtick_labels, tick_objs):
    if label in ['... ...', '34(min)']:
        text.set_rotation(0)
        text.set_ha('center')
    else:
        text.set_rotation(30)
        text.set_ha('center')

# 设置文本
for text, label in zip(tick_objs, xtick_labels):
    text.set_text(label)

# 应用修改后的刻度
plt.xticks(ticks=xtick_values, labels=xtick_labels, rotation=0)




# 9. 美化图形
plt.title('Histogram of House Prices', fontsize=16)
plt.xlabel('Price (×10,000 RMB)', fontsize=12)
plt.ylabel('Frequency', fontsize=12)
plt.grid(axis='y')  # 只显示水平网格线（取消垂直虚线）
plt.legend()
plt.tight_layout()

# 10. 显示图形
plt.show()
