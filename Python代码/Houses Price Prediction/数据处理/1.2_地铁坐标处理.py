import csv

# 输入的 CSV 文件路径
input_csv_file = '/Users/jia/Desktop/论文/数据/points.csv'  # 请替换为你的输入 CSV 文件路径
output_csv_file = '/Users/jia/Desktop/论文/数据/subway.csv'  # 输出的 CSV 文件路径

# 打开输入的 CSV 文件
with open(input_csv_file, 'r', encoding='utf-8') as csv_file:
    reader = csv.DictReader(csv_file)  # 使用 DictReader 来处理 CSV 文件

    # 获取 CSV 文件的字段名
    fieldnames = ['name', 'lon', 'lat']

    # 打开输出的 CSV 文件并写入筛选后的数据
    with open(output_csv_file, 'w', encoding='utf-8', newline='') as output_file:
        writer = csv.DictWriter(output_file, fieldnames=fieldnames)
        writer.writeheader()  # 写入表头

        # 遍历输入文件中的每一行，提取所需字段
        for row in reader:
            # 只写入 name, lon, lat 列
            filtered_row = {key: row[key] for key in fieldnames if key in row}
            writer.writerow(filtered_row)

print(f"数据已成功保存到 {output_csv_file}")
