import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
from matplotlib import font_manager

# ======================
# 1. 数据
# ======================
subsets = [
    "CD8+Ki67+",
    "CD8+GranzymeB+",
    "CD8+PD1+",
    "CD8+PDL1+",
    "CD8+PD1+PDL1+"
]

# 相对变化 = (卵巢转移灶 - 原发灶) / 原发灶 × 100%
relative_change = [-66, -86, -82, -82, -83]

# ======================
# 2. 输出路径：会覆盖原文件
# ======================
out_dir = Path("./figures")
out_dir.mkdir(exist_ok=True)

svg_path = out_dir / "figure_4_8_cd8_subset_relative_change.svg"
pdf_path = out_dir / "figure_4_8_cd8_subset_relative_change.pdf"
png_path = out_dir / "figure_4_8_cd8_subset_relative_change.png"

# ======================
# 3. 中文字体设置
# ======================
# Mac 常用中文字体候选
font_candidates = [
    "PingFang SC",
    "Songti SC",
    "Heiti SC",
    "Arial Unicode MS",
    "SimHei",
    "Microsoft YaHei"
]

available_fonts = {f.name for f in font_manager.fontManager.ttflist}
chosen_font = None

for font in font_candidates:
    if font in available_fonts:
        chosen_font = font
        break

if chosen_font is None:
    print("未找到常见中文字体，若中文乱码，请手动将 chosen_font 改为你电脑中的中文字体。")
    chosen_font = "sans-serif"

plt.rcParams["font.family"] = chosen_font
plt.rcParams["axes.unicode_minus"] = False

# 保证 PDF / SVG 文字尽量可编辑
plt.rcParams["pdf.fonttype"] = 42
plt.rcParams["ps.fonttype"] = 42
plt.rcParams["svg.fonttype"] = "none"

# ======================
# 4. 绘图
# ======================
fig, ax = plt.subplots(figsize=(8.6, 5.0))

y_pos = np.arange(len(subsets))

bars = ax.barh(
    y_pos,
    relative_change,
    height=0.55,
    color="#2F66C2",
    edgecolor="#244E99",
    linewidth=0.8
)

# 0 参考线
ax.axvline(
    0,
    color="black",
    linewidth=1.0,
    linestyle="--"
)

# 数值标签
for y, value in zip(y_pos, relative_change):
    ax.text(
        value - 2,
        y,
        f"{value}%",
        va="center",
        ha="right",
        fontsize=11,
        color="#1F4FA3"
    )

# 坐标轴
ax.set_yticks(y_pos)
ax.set_yticklabels(subsets, fontsize=11)
ax.invert_yaxis()

ax.set_xlim(-100, 5)
ax.set_xticks([-100, -80, -60, -40, -20, 0])

ax.set_xlabel("数量相对变化（%）", fontsize=12)
ax.set_ylabel("CD8 亚群", fontsize=12)

# 标题
ax.set_title(
    "CD8 亚群数量相对变化（卵巢转移灶 vs. 原发灶）",
    fontsize=15,
    pad=16
)

# 网格与边框
ax.grid(axis="x", linestyle="-", linewidth=0.5, alpha=0.35)
ax.set_axisbelow(True)

ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)

# 图内说明
fig.text(
    0.6,
    0.035,
    "相对变化 =（卵巢转移灶 − 原发灶）/ 原发灶 × 100%。",
    fontsize=9.5,
    ha="center",
    va="center"
)

plt.tight_layout(rect=[0, 0.08, 1, 1])

# ======================
# 5. 导出：覆盖原文件
# ======================
plt.savefig(svg_path, format="svg", bbox_inches="tight")
plt.savefig(pdf_path, format="pdf", bbox_inches="tight")
plt.savefig(png_path, dpi=600, bbox_inches="tight")

plt.close()

print(f"使用字体：{chosen_font}")
print(f"已覆盖保存 SVG：{svg_path}")
print(f"已覆盖保存 PDF：{pdf_path}")
print(f"已覆盖保存 PNG：{png_path}")