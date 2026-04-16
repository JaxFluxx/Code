import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# 1. 读取归一化后的CSV文件
file_path = r'/Users/jia/Desktop/学习 /机器学习/数据/1.4.csv'
df = pd.read_csv(file_path)

# 2. 确保 Payment_Code 是最后一列，调整列顺序
cols = list(df.columns)
if 'Payment_Code' in cols:
    cols.remove('Payment_Code')
    cols.append('Payment_Code')
df = df[cols]

# 3. 计算相关性矩阵
corr = df.corr()

# 4. 画热力图
plt.figure(figsize=(12, 10))
sns.heatmap(corr, annot=True, fmt=".2f", cmap='coolwarm', cbar=True, square=True,
            annot_kws={"size":8}, linewidths=0.5)

plt.title('Feature Correlation Heatmap')
plt.xticks(rotation=45, ha='right')
plt.yticks(rotation=0)
plt.tight_layout()
plt.show()
