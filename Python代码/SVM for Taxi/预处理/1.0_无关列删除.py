import pandas as pd

# 原始文件路径
file_path = r'/Users/jia/Desktop/学习 /机器学习/数据/1.0.csv'

# 读取数据
df = pd.read_csv(file_path)

# 要删除的列名列表（注意最后一列有两个空格）
columns_to_drop = [
    'Trip ID',
    'Taxi ID',
    'Trip Start Timestamp',
    'Pickup Census Tract',
    'Dropoff Census Tract',
    'Pickup Centroid Latitude',
    'Pickup Centroid Longitude',
    'Pickup Centroid Location',
    'Dropoff Centroid Latitude',
    'Dropoff Centroid Longitude',
    'Dropoff Centroid  Location'  # 注意：两个空格
]

# 删除列（存在则删除，不存在则跳过）
df_cleaned = df.drop(columns=[col for col in columns_to_drop if col in df.columns])

# 保存为新文件
output_path = r'/Users/jia/Desktop/学习 /机器学习/数据/1.1_删除列后.csv'
df_cleaned.to_csv(output_path, index=False)

print("\n✅ 已保存删除指定列后的文件：1.1.csv")
