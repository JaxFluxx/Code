import pandas as pd
import matplotlib.pyplot as plt

# 模拟分类报告输出
report_dict = {
    "Class": ["Non-Stroke", "Stroke", "Accuracy", "Macro Avg", "Weighted Avg", "", ""],
    "Precision": [0.84, 0.75, None, 0.80, 0.80, None, None],
    "Recall": [0.80, 0.80, None, 0.80, 0.80, None, None],
    "F1-Score": [0.82, 0.77, 0.80, 0.80, 0.80, None, None],
    "Support": [100, 75, 175, 175, 175, None, None]
}

# 创建 DataFrame，并删除最后两行
report_df = pd.DataFrame(report_dict).iloc[:-2]

# 保留两位小数并转为字符串
for col in ["Precision", "Recall", "F1-Score"]:
    report_df[col] = report_df[col].apply(lambda x: f"{x:.2f}" if pd.notnull(x) else "/")

# Support 转为整数字符串
report_df["Support"] = report_df["Support"].apply(lambda x: f"{int(x)}" if pd.notnull(x) else "/")

# 图像设置
plt.figure(figsize=(10, 4.5))
plt.text(0.5, 0.85, "SVM Classification Report", fontsize=14, weight='bold', ha='center')
plt.axis('off')

# 创建表格
table = plt.table(cellText=report_df.values,
                  colLabels=report_df.columns,
                  cellLoc='center',
                  loc='center',
                  colColours=["#f2f2f2"]*len(report_df.columns))

table.auto_set_font_size(False)
table.set_fontsize(12)
table.scale(1.2, 1.5)

# 计算表格下边界（视觉靠紧贴）
# 减少 y 值使其更贴近
plt.text(-0.1, 0.1, 'Accuracy: 0.80', fontsize=12, color='black', ha='left')
plt.text(-0.1, 0.19, 'Total Recall: 0.80', fontsize=12, color='black', ha='left')

# Figure 9 标题下沉并居中
plt.text(0.5, -0.01, 'Figure 3', fontsize=12, ha='center', style='italic')

# 调整布局
plt.tight_layout()
# plt.savefig("svm_classification_report_final_v3.png", dpi=300)
plt.show()
