import pandas as pd
from mlxtend.frequent_patterns import apriori, association_rules
from mlxtend.preprocessing import TransactionEncoder
import matplotlib.pyplot as plt
import seaborn as sns

plt.rcParams['font.sans-serif'] = ['Arial Unicode MS'] #苹果系统显示中文字体

# 数据集路径
file_path = "data/groceries_dataset.csv"

# 1. 数据预处理
# 读取数据集
df = pd.read_csv(file_path)

# 查看数据集的前几行
print("数据集的前几行：")
print(df.head())

# 将数据转换为适合频繁模式挖掘的事务数据集
# 按照 Member_number 和 Date 分组，收集每个消费者在每次交易中购买的商品
transactions = df.groupby(['Member_number', 'Date'])['itemDescription'].apply(list).reset_index()

# 查看处理后的事务数据集
print("\n处理后的事务数据集：")
print(transactions.head())

# 2. 频繁项集挖掘
# 使用 TransactionEncoder 将事务数据转换为布尔矩阵
te = TransactionEncoder()
te_ary = te.fit(transactions['itemDescription']).transform(transactions['itemDescription'])
df_encoded = pd.DataFrame(te_ary, columns=te.columns_)

# 使用 Apriori 算法挖掘频繁项集，最小支持度设置为 0.005
frequent_itemsets = apriori(df_encoded, min_support=0.005, use_colnames=True)

# 输出频繁项集
print("\n频繁项集：")
print(frequent_itemsets)

# 3. 关联规则挖掘
# 生成关联规则，计算支持度、置信度和提升度，最小置信度设置为 0.08
rules = association_rules(frequent_itemsets, metric="confidence", min_threshold=0.08)

# 输出关联规则
print("\n关联规则：")
print(rules)

# 4. 多样性分析
# 分析消费者的购买频率
# 计算每个消费者的购买次数
purchase_counts = df['Member_number'].value_counts()

# 创建高频与低频购买者的分界线
threshold = purchase_counts.quantile(0.5)  # 计算中位数作为阈值
high_freq = purchase_counts[purchase_counts > threshold].index.tolist()
low_freq = purchase_counts[purchase_counts <= threshold].index.tolist()

# 分析高频购买者和低频购买者的购买行为
high_freq_purchases = df[df['Member_number'].isin(high_freq)]
low_freq_purchases = df[df['Member_number'].isin(low_freq)]

# 查看高频购买者和低频购买者购买的商品数量
high_freq_items = high_freq_purchases['itemDescription'].value_counts().head(10)  # 高频购买者前10商品
low_freq_items = low_freq_purchases['itemDescription'].value_counts().head(10)    # 低频购买者前10商品

# 可视化高频与低频购买者的购买行为
plt.figure(figsize=(12, 6))
sns.barplot(x=high_freq_items.index, y=high_freq_items.values, color='blue', alpha=0.7, label='高频购买者')
sns.barplot(x=low_freq_items.index, y=low_freq_items.values, color='red', alpha=0.5, label='低频购买者')
plt.xticks(rotation=90)
plt.title("高频与低频购买者的商品购买对比")
plt.xlabel("商品")
plt.ylabel("购买次数")
plt.legend()
plt.tight_layout()
plt.show()
