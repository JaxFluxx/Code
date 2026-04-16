import pandas as pd
import matplotlib.pyplot as plt

# 假设你的文件名是 'taxi_data.csv'
df = pd.read_csv('/Users/jia/Desktop/学习 /机器学习/数据/1.3.csv')

# 去除Date列可能存在的空格
df['Date'] = df['Date'].astype(str).str.strip()

# 定义美国重要节假日（中文格式对应）
us_holidays = [
    "1月1日",    # 新年
    "7月4日",    # 独立日
    "9月2日",    # 劳动节
    "11月28日",  # 感恩节
    "12月25日",  # 圣诞节
    "12月31日"   # 新年前夜
]

# 标记是否节假日
df['Is_Holiday'] = df['Date'].isin(us_holidays)

# 计算支付方式占比（百分比）
holiday_payment = df[df['Is_Holiday']]['Payment Type'].value_counts(normalize=True) * 100
nonholiday_payment = df[~df['Is_Holiday']]['Payment Type'].value_counts(normalize=True) * 100

# 合并结果
compare_df = pd.DataFrame({
    'Holiday': holiday_payment,
    'Non-Holiday': nonholiday_payment
}).fillna(0)

print("支付方式在节假日 vs 非节假日中的占比（%）：")
print(compare_df)

# 画图对比
compare_df.plot(kind='bar', figsize=(8,5))
plt.title('Payment Type Comparison: Holiday vs Non-Holiday')
plt.ylabel('Percentage (%)')
plt.xticks(rotation=0)
plt.tight_layout()
plt.show()
