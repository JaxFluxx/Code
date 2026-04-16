# -*- coding: utf-8 -*-
"""
精简版：数据集探索可视化（整合最终版）
输出目录：
/Users/jia/Desktop/学习 /毕业设计/实验/数据集探索

保留内容：
- 图1：样本与配对总体概览（3D风格饼图）
- 图2：代表性样本对的 Tumor / M1 / M2 细胞组成图（1个R对 + 1个L对）
- 图3：模糊巨噬细胞筛除统计（数量 + 比例）
- 表1：数据集与配对概览
- 表2：样本探索汇总表
- 终端输出关键统计

说明：
1）文本表格统一 utf-8-sig 编码，方便 Excel 直接打开
2）百分比保留两位小数；其他数字保留4位有效数字
3）当前“模糊细胞筛除平衡性”只做探索统计，不做校正
"""

from pathlib import Path
import shutil
import re
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# =========================
# 0) matplotlib 字体设置（Mac）
# =========================
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['figure.dpi'] = 140

# =========================
# 1) 路径设置
# =========================
ROOT = Path("/Users/jia/Desktop/学习 /毕业设计/实验")
CLEAN_ROOT = ROOT / "CODEX_clean_baseline"
OUT_DIR = ROOT / "数据集探索"

sample_summary_path = CLEAN_ROOT / "sample_summary.tsv"
pair_manifest_path = CLEAN_ROOT / "pair_manifest.tsv"

if not sample_summary_path.exists():
    raise FileNotFoundError(f"找不到 sample_summary.tsv：{sample_summary_path}")
if not pair_manifest_path.exists():
    raise FileNotFoundError(f"找不到 pair_manifest.tsv：{pair_manifest_path}")

# 覆盖旧目录
if OUT_DIR.exists():
    shutil.rmtree(OUT_DIR)
OUT_DIR.mkdir(parents=True, exist_ok=True)

SUMMARY_DIR = OUT_DIR / "表格汇总"
FIG1_DIR = OUT_DIR / "图1_样本与配对概览"
FIG2_DIR = OUT_DIR / "图2_代表性样本对细胞组成"
FIG3_DIR = OUT_DIR / "图3_模糊巨噬细胞筛除统计"

for d in [SUMMARY_DIR, FIG1_DIR, FIG2_DIR, FIG3_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# =========================
# 2) 读入基础表
# =========================
sample_summary = pd.read_csv(sample_summary_path, sep="\t")
pair_manifest = pd.read_csv(pair_manifest_path, sep="\t")

# =========================
# 3) 辅助函数
# =========================
def parse_sample_suffix(sample_name: str):
    s = str(sample_name).strip()
    if s.endswith("QT"):
        return "QT"
    if s.endswith("P"):
        return "P"
    if s.endswith("L"):
        return "L"
    if s.endswith("R"):
        return "R"
    return "Unknown"

def parse_patient_id(sample_name: str):
    m = re.match(r"^(\d+)", str(sample_name).strip())
    return int(m.group(1)) if m else np.nan

def safe_div(a, b):
    if b is None or pd.isna(b) or b == 0:
        return np.nan
    return a / b

def fmt_sig4(x):
    """其他数字保留4位有效数字"""
    if pd.isna(x):
        return ""
    x = float(x)
    if x == 0:
        return "0"
    return f"{x:.4g}"

def fmt_pct(x):
    """百分比保留两位小数"""
    if pd.isna(x):
        return ""
    return f"{float(x) * 100:.2f}%"

def export_tsv_excel_friendly(df: pd.DataFrame, path: Path, percent_cols=None):
    """
    导出为 Excel 友好的 utf-8-sig TSV
    百分比列转为百分号字符串；其他数值列转为4位有效数字字符串
    """
    percent_cols = percent_cols or []
    out = df.copy()

    for c in out.columns:
        if c in percent_cols:
            out[c] = out[c].map(fmt_pct)
        elif pd.api.types.is_numeric_dtype(out[c]):
            out[c] = out[c].map(fmt_sig4)

    out.to_csv(path, sep="\t", index=False, encoding="utf-8-sig")

def sample_group_from_suffix(s):
    if s == "P":
        return "Primary"
    if s == "L":
        return "L"
    if s == "R":
        return "R"
    if s == "QT":
        return "QT"
    return "Unknown"

# 颜色
COLOR_TUMOR = "#4D4D4D"
COLOR_M1 = "#4C78A8"
COLOR_M2 = "#E45756"
COLOR_AMB = "#9C755F"

# =========================
# 4) 补充样本信息：样本组别 / 模糊巨噬统计
# =========================
sample_summary["sample_suffix"] = sample_summary["sample_name"].apply(parse_sample_suffix)
sample_summary["patient_id"] = sample_summary["sample_name"].apply(parse_patient_id)
sample_summary["sample_group"] = sample_summary["sample_suffix"].apply(sample_group_from_suffix)

ambiguous_rows = []

for _, row in sample_summary.iterrows():
    clean_path = Path(row["clean_all_path"])
    amb_n = np.nan
    amb_ratio = np.nan
    mac_total = np.nan

    if clean_path.exists():
        df = pd.read_csv(clean_path, sep="\t")
        if "cell_type" in df.columns:
            amb_n = int((df["cell_type"] == "Ambiguous_Mac").sum())
        if "is_mac" in df.columns:
            mac_total = int((df["is_mac"] == 1).sum())
        amb_ratio = safe_div(amb_n, mac_total)

    ambiguous_rows.append({
        "sample_name": row["sample_name"],
        "ambiguous_mac_n": amb_n,
        "all_mac_n_for_denominator": mac_total,
        "ambiguous_mac_ratio": amb_ratio
    })

ambiguous_df = pd.DataFrame(ambiguous_rows)
explore_df = sample_summary.merge(ambiguous_df, on="sample_name", how="left")

# 给 pair_manifest 补组别
pair_manifest["met_group"] = pair_manifest["met_sample"].apply(parse_sample_suffix)

# =========================
# 5) 表1：数据集与配对概览表
# =========================
sample_counts = (
    explore_df["sample_group"]
    .value_counts()
    .reindex(["Primary", "L", "R", "QT"])
    .fillna(0)
    .astype(int)
)

pair_counts = (
    pair_manifest["met_group"]
    .value_counts()
    .reindex(["L", "R", "QT"])
    .fillna(0)
    .astype(int)
)

overview_table = pd.DataFrame({
    "项目": [
        "总样本数",
        "Primary样本数", "L样本数", "R样本数", "QT样本数",
        "总配对数",
        "P-L配对数", "P-R配对数", "P-QT配对数"
    ],
    "数值": [
        int(len(explore_df)),
        int(sample_counts.get("Primary", 0)),
        int(sample_counts.get("L", 0)),
        int(sample_counts.get("R", 0)),
        int(sample_counts.get("QT", 0)),
        int(len(pair_manifest)),
        int(pair_counts.get("L", 0)),
        int(pair_counts.get("R", 0)),
        int(pair_counts.get("QT", 0)),
    ]
})

export_tsv_excel_friendly(
    overview_table,
    SUMMARY_DIR / "表1_数据集与配对概览.tsv",
    percent_cols=[]
)

# =========================
# 6) 表2：样本探索汇总表
# =========================
sample_explore_table = explore_df[[
    "patient_id", "sample_name", "sample_group",
    "tumor_n", "m1_n", "m2_n",
    "m2_frac_of_mac",
    "ambiguous_mac_n", "all_mac_n_for_denominator", "ambiguous_mac_ratio"
]].copy()

sample_explore_table = sample_explore_table.sort_values(
    ["sample_group", "patient_id", "sample_name"]
).reset_index(drop=True)

export_tsv_excel_friendly(
    sample_explore_table,
    SUMMARY_DIR / "表2_样本探索汇总表.tsv",
    percent_cols=["m2_frac_of_mac", "ambiguous_mac_ratio"]
)

# =========================
# 7) 图1：样本与配对总体概览（3D风格饼图）
# =========================
fig, axes = plt.subplots(1, 2, figsize=(11.5, 5.2))

# 左：样本构成
sample_labels = ["Primary", "L", "R", "QT"]
sample_sizes = [sample_counts.get(x, 0) for x in sample_labels]
sample_explode = [0.03, 0.05, 0.08, 0.05]

axes[0].pie(
    sample_sizes,
    labels=sample_labels,
    autopct="%1.1f%%",
    startangle=90,
    explode=sample_explode,
    shadow=True,
    wedgeprops={"linewidth": 1, "edgecolor": "white"}
)
axes[0].set_title("样本类型构成")

# 右：配对构成
pair_labels = ["P-L", "P-R", "P-QT"]
pair_sizes = [
    pair_counts.get("L", 0),
    pair_counts.get("R", 0),
    pair_counts.get("QT", 0),
]
pair_explode = [0.05, 0.10, 0.05]

axes[1].pie(
    pair_sizes,
    labels=pair_labels,
    autopct="%1.1f%%",
    startangle=90,
    explode=pair_explode,
    shadow=True,
    wedgeprops={"linewidth": 1, "edgecolor": "white"}
)
axes[1].set_title("配对类型构成")

plt.suptitle("图1 数据集与配对总体概览", fontsize=14)
plt.tight_layout()
plt.savefig(FIG1_DIR / "图1_数据集与配对总体概览_3D风格饼图.png", bbox_inches="tight")
plt.close()

# =========================
# 8) 图2：代表性样本对的细胞组成
# 只挑 1 个 R 对 + 1 个 L 对
# =========================
pair_plot_rows = []

# 挑一个 R 样本对：优先转移灶 tumor_n 大的
r_pairs = pair_manifest[pair_manifest["met_group"] == "R"].copy()
if len(r_pairs) > 0:
    r_pairs["met_tumor_n"] = r_pairs["met_sample"].map(
        dict(zip(explore_df["sample_name"], explore_df["tumor_n"]))
    )
    r_pick = r_pairs.sort_values("met_tumor_n", ascending=False).iloc[0]
    pair_plot_rows.append(r_pick)

# 挑一个 L 样本对：优先转移灶 tumor_n 大的
l_pairs = pair_manifest[pair_manifest["met_group"] == "L"].copy()
if len(l_pairs) > 0:
    l_pairs["met_tumor_n"] = l_pairs["met_sample"].map(
        dict(zip(explore_df["sample_name"], explore_df["tumor_n"]))
    )
    l_pick = l_pairs.sort_values("met_tumor_n", ascending=False).iloc[0]
    pair_plot_rows.append(l_pick)

pair_plot_df = pd.DataFrame(pair_plot_rows)

if len(pair_plot_df) > 0:
    n_pairs = len(pair_plot_df)
    fig, axes = plt.subplots(n_pairs, 2, figsize=(10, 4.2 * n_pairs))
    if n_pairs == 1:
        axes = np.array([axes])

    for row_idx, (_, pr) in enumerate(pair_plot_df.iterrows()):
        for col_idx, sample_col in enumerate(["primary_sample", "met_sample"]):
            sample_name = pr[sample_col]
            srow = explore_df[explore_df["sample_name"] == sample_name].iloc[0]

            tumor_n = srow["tumor_n"]
            m1_n = srow["m1_n"]
            m2_n = srow["m2_n"]

            ax = axes[row_idx, col_idx]
            vals = [tumor_n, m1_n, m2_n]
            labels = ["Tumor", "M1", "M2"]
            colors = [COLOR_TUMOR, COLOR_M1, COLOR_M2]

            ax.bar(labels, vals, color=colors)
            ax.set_title(f"{sample_name} 细胞组成")
            ax.set_ylabel("细胞数")
            ymax = max(vals) if max(vals) > 0 else 1
            for i, v in enumerate(vals):
                if pd.notna(v):
                    ax.text(i, v + ymax * 0.02, f"{int(v)}", ha="center", fontsize=9)

    plt.suptitle("图2 代表性样本对的 Tumor / M1 / M2 细胞组成", fontsize=14)
    plt.tight_layout()
    plt.savefig(FIG2_DIR / "图2_代表性样本对_Tumor_M1_M2_细胞组成.png", bbox_inches="tight")
    plt.close()

    pair_plot_df.to_csv(
        SUMMARY_DIR / "代表性样本对清单.tsv",
        sep="\t",
        index=False,
        encoding="utf-8-sig"
    )

# =========================
# 9) 图3：模糊巨噬细胞筛除统计
# =========================
plot_amb = explore_df.sort_values(["sample_group", "patient_id", "sample_name"]).reset_index(drop=True)
x = np.arange(len(plot_amb))

fig, axes = plt.subplots(1, 2, figsize=(14, 4.8))

# 左：数量
axes[0].bar(x, plot_amb["ambiguous_mac_n"].fillna(0).values, color=COLOR_AMB)
axes[0].set_xticks(x)
axes[0].set_xticklabels(plot_amb["sample_name"], rotation=70)
axes[0].set_title("各样本模糊巨噬细胞数量")
axes[0].set_ylabel("Ambiguous_Mac 数量")

# 右：比例
amb_ratio_pct = plot_amb["ambiguous_mac_ratio"].fillna(0) * 100.0
axes[1].bar(x, amb_ratio_pct.values, color=COLOR_AMB)
axes[1].set_xticks(x)
axes[1].set_xticklabels(plot_amb["sample_name"], rotation=70)
axes[1].set_title("各样本模糊巨噬细胞比例")
axes[1].set_ylabel("占全部巨噬比例 (%)")

plt.suptitle("图3 模糊巨噬细胞筛除统计", fontsize=14)
plt.tight_layout()
plt.savefig(FIG3_DIR / "图3_模糊巨噬细胞筛除统计.png", bbox_inches="tight")
plt.close()

# =========================
# 10) 终端输出关键统计
# =========================
print("\n================= 数据集探索：关键统计输出 =================")

print("\n[1] 样本与配对统计")
print(f"总样本数: {len(explore_df)}")
print(f"Primary样本数: {int(sample_counts.get('Primary', 0))}")
print(f"L样本数: {int(sample_counts.get('L', 0))}")
print(f"R样本数: {int(sample_counts.get('R', 0))}")
print(f"QT样本数: {int(sample_counts.get('QT', 0))}")
print(f"总配对数: {len(pair_manifest)}")
print(f"P-L配对数: {int(pair_counts.get('L', 0))}")
print(f"P-R配对数: {int(pair_counts.get('R', 0))}")
print(f"P-QT配对数: {int(pair_counts.get('QT', 0))}")

print("\n[2] 模糊巨噬细胞整体统计")
total_amb = explore_df["ambiguous_mac_n"].fillna(0).sum()
total_mac = explore_df["all_mac_n_for_denominator"].fillna(0).sum()
overall_amb_ratio = safe_div(total_amb, total_mac)

print(f"全部样本 Ambiguous_Mac 总数: {fmt_sig4(total_amb)}")
print(f"全部样本用于分母的巨噬总数: {fmt_sig4(total_mac)}")
print(f"整体模糊巨噬比例: {fmt_pct(overall_amb_ratio)}")

print("\n各组模糊巨噬比例（均值 / 中位数）")
for g in ["Primary", "L", "R", "QT"]:
    vals = explore_df.loc[explore_df["sample_group"] == g, "ambiguous_mac_ratio"].dropna()
    if len(vals):
        print(f"- {g:8s} 均值={fmt_pct(vals.mean())}  中位数={fmt_pct(vals.median())}  n={len(vals)}")
    else:
        print(f"- {g:8s} 无数据")

print("\n[3] 模糊巨噬比例最高的前5个样本")
top5 = explore_df.sort_values("ambiguous_mac_ratio", ascending=False).head(5)
for _, r in top5.iterrows():
    print(
        f"- {r['sample_name']:6s} | group={r['sample_group']:7s} | "
        f"amb_n={fmt_sig4(r['ambiguous_mac_n'])} | "
        f"amb_ratio={fmt_pct(r['ambiguous_mac_ratio'])}"
    )

print("\n[4] 代表性样本对")
if len(pair_plot_df) > 0:
    for _, r in pair_plot_df.iterrows():
        print(
            f"- 病人{int(r['patient_id'])}: {r['primary_sample']} vs {r['met_sample']}"
        )
else:
    print("未找到可用代表性样本对")

print("\n✅ 输出完成")
print(f"输出目录：{OUT_DIR}")
print(f"- 表1：{SUMMARY_DIR / '表1_数据集与配对概览.tsv'}")
print(f"- 表2：{SUMMARY_DIR / '表2_样本探索汇总表.tsv'}")
if len(pair_plot_df) > 0:
    print(f"- 代表性样本对清单：{SUMMARY_DIR / '代表性样本对清单.tsv'}")
print(f"- 图1：{FIG1_DIR / '图1_数据集与配对总体概览_3D风格饼图.png'}")
if len(pair_plot_df) > 0:
    print(f"- 图2：{FIG2_DIR / '图2_代表性样本对_Tumor_M1_M2_细胞组成.png'}")
print(f"- 图3：{FIG3_DIR / '图3_模糊巨噬细胞筛除统计.png'}")