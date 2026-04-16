import pandas as pd
import matplotlib.pyplot as plt

# 读取 CSV 文件
file_path = '/Users/jia/Desktop/论文/数据/数据处理/北京二手房成交_1.1_en.csv'
df = pd.read_csv(file_path)

# 统计每一列中“暂无数据”的比例
missing_data = []

for col in df.columns:
    total = len(df[col])
    missing_count = (df[col] == '暂无数据').sum()
    ratio = missing_count / total
    if ratio > 0:
        missing_data.append({'Feature': col, 'Ratio': ratio})

# 构建 DataFrame 并排序
missing_df = pd.DataFrame(missing_data)
missing_df = missing_df.sort_values(by='Ratio', ascending=False)

# 打印表格到终端
print("=== 每列中“暂无数据”的比例（不为0） ===")
print(missing_df.to_string(index=False, formatters={'Ratio': '{:.2%}'.format}))

# 绘制表格图片
fig, ax = plt.subplots(figsize=(8, len(missing_df) * 0.5 + 2))
ax.axis('off')

# 添加标题
plt.title('Table of the proportion of missing feature values', fontsize=14, y=0.8, fontweight='bold')

# 添加表格
table = ax.table(
    cellText=[[row['Feature'], f"{row['Ratio']:.2%}"] for _, row in missing_df.iterrows()],
    colLabels=['Feature', 'Ratio'],
    loc='center',
    cellLoc='center'
)
table.auto_set_font_size(False)
table.set_fontsize(10)
table.scale(1, 1.5)

# 加粗表头字体
for key, cell in table.get_celld().items():
    if key[0] == 0:  # 表头所在的行索引为0
        cell.set_text_props(weight='bold')

# 显示图像
plt.show()

# 保存图片（如需要）
# plt.savefig('missing_data_table.png', bbox_inches='tight', dpi=300)
