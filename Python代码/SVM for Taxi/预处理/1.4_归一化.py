import pandas as pd
import numpy as np
from datetime import datetime

# 1. 读取数据
file_path = r'/Users/jia/Desktop/学习 /机器学习/数据/1.3.csv'
df = pd.read_csv(file_path)

# 2. 将“X月X日”转为“MM/DD”
def chinese_date_to_mmdd(ch_date):
    try:
        ch_date = ch_date.replace('月', '/').replace('日', '')
        parts = ch_date.split('/')
        mm = parts[0].zfill(2)
        dd = parts[1].zfill(2)
        return f"{mm}/{dd}"
    except:
        return None

df['Date'] = df['Date'].apply(chinese_date_to_mmdd)

# 3. 转为一年中的第几天（1~365）并归一化
df['day_of_year'] = df['Date'].apply(lambda x: datetime.strptime(x + '/2024', '%m/%d/%Y').timetuple().tm_yday)
df['day_normalized'] = df['day_of_year'] / 365

# 4. 数值列标准化（Z-score）
numeric_cols = ['Trip Seconds', 'Trip Miles', 'Pickup Community Area', 'Dropoff Community Area',
                'Fare', 'Tips', 'Tolls', 'Extras', 'Trip Total', 'Hour']

for col in numeric_cols:
    df[col + '_z'] = (df[col] - df[col].mean()) / df[col].std()

# 5. Payment Type 编码（0: Cash, 1: Credit Card）
df['Payment_Code'] = df['Payment Type'].map({'Cash': 0, 'Credit Card': 1})

# 6. Company 编码：按出现顺序编号，然后归一化
company_list = df['Company'].dropna().unique()
company_mapping = {name: idx for idx, name in enumerate(company_list)}
df['Company_Code'] = df['Company'].map(company_mapping)
df['Company_Code_Normalized'] = df['Company_Code'] / df['Company_Code'].max()

# 7. 准备输出列
final_cols = [col + '_z' for col in numeric_cols] + ['day_normalized', 'Payment_Code', 'Company_Code_Normalized']
df_final = df[final_cols]

# 8. 保存处理后的 CSV
output_path = r'/Users/jia/Desktop/学习 /机器学习/数据/1.5.csv'
df_final.to_csv(output_path, index=False)

print("✅ 所有数据归一化处理完毕，文件保存为 1.4.csv")

# 9. 输出编码映射表
print("\n📘 Payment Type 编码：")
print("Cash -> 0\nCredit Card -> 1")

print("\n📘 Company 编码对应表：")
for name, code in company_mapping.items():
    print(f"{name} -> {code}")
