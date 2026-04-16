import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS']

# 1. 读取数据
df = pd.read_csv('/Users/jia/Desktop/论文/数据/数据处理/北京二手房成交_1.8.csv')

# 2. 删除第一列（id列），不进行分析
df = df.drop(columns=['id'], errors='ignore')

# 3. 计算相关性矩阵
correlation_matrix = df.corr()

# 4. 绘制热力图
plt.figure(figsize=(16, 12))
sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', cbar=True, linewidths=0.5)
plt.title('Feature Correlation Heatmap', fontsize=24, fontweight='bold')
plt.xticks(fontsize=14)
plt.yticks(fontsize=14)
plt.tight_layout()
plt.show()
