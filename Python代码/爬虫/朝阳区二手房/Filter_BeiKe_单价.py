import pandas as pd
import os

# 读取Excel文件
file_path = r"C:\Users\何嘉\Desktop\朝阳二手房贝壳\朝阳二手房数据_贝壳网_原始.test.xlsx"
df = pd.read_excel(file_path)

# 过滤出不同层级的数据
df_20000_40000 = df[(df['单价(元/平米)'] >= 20000) & (df['单价(元/平米)'] < 40000)]
df_40000_80000 = df[(df['单价(元/平米)'] >= 40000) & (df['单价(元/平米)'] < 80000)]
df_above_80000 = df[df['单价(元/平米)'] >= 80000]

# 定义文件夹路径
base_dir = r"C:\Users\何嘉\Desktop\朝阳二手房贝壳"
folders = ["20000_40000", "40000_80000", "above_80000"]

# 创建文件夹
for folder in folders:
    folder_path = os.path.join(base_dir, folder)
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

# 保存到不同的文件夹中
df_20000_40000.to_excel(os.path.join(base_dir, "20000_40000", "20000_40000.xlsx"), index=False)
df_40000_80000.to_excel(os.path.join(base_dir, "40000_80000", "40000_80000.xlsx"), index=False)
df_above_80000.to_excel(os.path.join(base_dir, "above_80000", "above_80000.xlsx"), index=False)

print("数据已成功过滤并保存到相应的文件夹中。")
