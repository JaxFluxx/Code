import pandas as pd

# ========== 读取 CSV 文件 ==========
file_path = r'/Users/jia/Desktop/学习 /机器学习/数据/1.3.csv'
df = pd.read_csv(file_path)

# ========== 处理 Date 列为 datetime 格式 ==========
# 如果是“1月1日”这样的格式，补上年份（例如默认 2024 年）
df['Date'] = pd.to_datetime('2024年' + df['Date'], format='%Y年%m月%d日', errors='coerce')

# ========== 统计时间范围 ==========
min_date = df['Date'].min()
max_date = df['Date'].max()

# ========== 列出所有字段名 ==========
columns = df.columns.tolist()

# ========== 统计数据规模 ==========
num_rows, num_columns = df.shape

# ========== 打印结果 ==========
print("🕒 数据时间范围（Date 列）：")
print(f"最早时间：{min_date.date()}")
print(f"最晚时间：{max_date.date()}\n")

print("🧾 包含的变量（字段）：")
for i, col in enumerate(columns, 1):
    print(f"{i}. {col}")
print()

print("📊 数据规模：")
print(f"记录条数（rows）：{num_rows}")
print(f"变量个数（columns）：{num_columns}")
