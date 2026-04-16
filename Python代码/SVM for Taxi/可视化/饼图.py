import pandas as pd
import matplotlib.pyplot as plt

plt.rcParams['font.sans-serif'] = ['Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题

# 读取CSV文件
file_path = '/Users/jia/Desktop/学习 /机器学习/数据/1.3.csv'
df = pd.read_csv(file_path)

# 统计每种支付方式的频数
payment_counts = df['Payment Type'].value_counts()

# 设置颜色（可选）
colors = plt.cm.Set3.colors[:len(payment_counts)]

# 设置字体大小
plt.rcParams['font.size'] = 16  # 全局字体大小

# 模拟伪3D效果：设置 explode 让主类别凸出
explode = [0.1 if i == 0 else 0 for i in range(len(payment_counts))]  # 主类突出

# 绘图
plt.figure(figsize=(8, 6))
wedges, texts, autotexts = plt.pie(
    payment_counts,
    labels=payment_counts.index,
    autopct='%1.1f%%',
    startangle=120,
    colors=colors,
    explode=explode,
    shadow=True,
    textprops={'fontsize': 18}
)

# 添加图例
plt.legend(wedges, payment_counts.index, title='支付方式', loc='upper left', fontsize=12, title_fontsize=13)

# 添加标题
plt.title('支付方式分布饼图', fontsize=20)

# 保持为正圆形
plt.axis('equal')

plt.tight_layout()
plt.show()
