import pandas as pd

# 读取 CSV 文件
file_path = '/Users/jia/Desktop/论文/数据/数据处理/北京二手房成交_1.5.csv'
df = pd.read_csv(file_path)

# 不需要列举属性值的列
exclude_columns = ['商圈', '小区', '经度', '纬度', '建筑面积（㎡）', '建成年代', '价格', 'id']

# 要列举属性值的列
categorical_columns = [col for col in df.columns if col not in exclude_columns]

print("=== 属性值统计与列举 ===")
for col in categorical_columns:
    unique_values = df[col].dropna().unique()
    print(f"\n列名：{col}")
    print(f"属性值个数：{len(unique_values)}")
    print("属性值如下：", end="")
    print(", ".join(map(str, unique_values)))

# 数值型列：输出范围
numerical_columns = ['建筑面积（㎡）', '建成年代', '价格', '建筑面积（㎡）']
print("\n=== 数值范围统计 ===")
for col in numerical_columns:
    min_val = df[col].min()
    max_val = df[col].max()
    print(f"{col}：{min_val} ~ {max_val}")

# 统计 exclude_columns 列的属性值个数
print("\n=== 额外列属性值个数统计 ===")
for col in exclude_columns:
    unique_values = df[col].dropna().unique()
    print(f"\n列名：{col}")
    print(f"属性值个数：{len(unique_values)}")