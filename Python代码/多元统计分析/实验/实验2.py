#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pandas.plotting import scatter_matrix

# ---- Read CSV (handle '\ ' in your path) ----
path_raw = r"/Users/jia/Desktop/学习\ /多元统计分析/实验1/Iris数据集/iris.csv"
csv_path = path_raw if os.path.exists(path_raw) else path_raw.replace(r"\ ", " ")
df = pd.read_csv(csv_path, encoding="utf-8")

feature_cols = ["Sepal.Length", "Sepal.Width", "Petal.Length", "Petal.Width"]
species_col = next((c for c in df.columns if c.lower() == "species"), "Species")
assert set(feature_cols).issubset(df.columns), "CSV must contain the 4 numeric Iris columns."

# unify species labels
mapping = {"山鸢尾": "setosa", "变色鸢尾": "versicolor", "维吉尼亚鸢尾": "virginica"}
df[species_col] = df[species_col].replace(mapping).str.lower()

# add 1-based row ID for legend display
if "_RowID" not in df.columns:
    df["_RowID"] = np.arange(1, len(df) + 1)

# ---- 1) Boxplot: Petal.Length by species (ID 19 -> remainder 3) ----
target_var = "Petal.Length"
fig1, ax1 = plt.subplots(figsize=(5, 9), dpi=120)
groups, labels = [], []
for name, g in df.groupby(species_col):
    groups.append(g[target_var].values)
    labels.append(name.capitalize())
bp = ax1.boxplot(groups, labels=labels, patch_artist=True, medianprops=dict(linewidth=2))
for box in bp["boxes"]:
    box.set_alpha(0.4)
ax1.set_title(f"Boxplot of {target_var} by Species")
ax1.set_xlabel("Species")
ax1.set_ylabel(target_var)
ax1.grid(True, linestyle="--", alpha=0.3)
#plt.tight_layout()


import seaborn as sns

# 统一物种标签的首字母大写，便于图例显示
df[species_col] = df[species_col].str.lower().map({
    "setosa":"I. setosa", "versicolor":"I. versicolor", "virginica":"I. virginica"
})

# 自定义调色（可用你原来的 color_map）
palette = {"I. setosa":"#1f77b4", "I. versicolor":"#ff7f0e", "I. virginica":"#2ca02c"}

g = sns.pairplot(
    df,
    vars=feature_cols,
    hue=species_col,
    diag_kind="kde",                # 对角线用 KDE
    palette=palette,
    plot_kws=dict(alpha=0.8, s=30), # 散点透明度/尺寸
    diag_kws=dict(common_norm=False, fill=False, lw=1.8)  # 关键：每类各自归一化 → 三条独立曲线
)
g.fig.suptitle("Iris Pairwise Plots with Class-wise KDE", y=1.02)
plt.show()

# ---- 2) Radar chart: one sample per species (legend shows row ID) ----
def pick_row_by_petal_length(g: pd.DataFrame, mode: str) -> pd.Series:
    if mode == "min":
        idx = g[target_var].idxmin()
    elif mode == "median":
        med = g[target_var].median()
        idx = (g[target_var] - med).abs().idxmin()
    elif mode == "max":
        idx = g[target_var].idxmax()
    else:
        idx = g.index[0]
    return g.loc[idx]

row_setosa     = pick_row_by_petal_length(df[df[species_col] == "setosa"], "min")
row_versicolor = pick_row_by_petal_length(df[df[species_col] == "versicolor"], "median")
row_virginica  = pick_row_by_petal_length(df[df[species_col] == "virginica"], "max")

# normalize 0–1 across the whole dataset
mins = df[feature_cols].min()
maxs = df[feature_cols].max()
def norm_values(row: pd.Series):
    return ((row[feature_cols] - mins) / (maxs - mins)).values.tolist()

labels_feat = ["Sepal.Len", "Sepal.Wid", "Petal.Len", "Petal.Wid"]
angles = np.linspace(0, 2*np.pi, len(labels_feat), endpoint=False).tolist()
angles += angles[:1]

def add_radar(ax, values, label):
    vals = values + values[:1]
    ax.plot(angles, vals, linewidth=2, label=label)
    ax.fill(angles, vals, alpha=0.15)

fig2 = plt.figure(figsize=(6.6, 6.6), dpi=120)
ax2 = plt.subplot(111, polar=True)
add_radar(ax2, norm_values(row_setosa),     f"Setosa (ID: {int(row_setosa['_RowID'])})")
add_radar(ax2, norm_values(row_versicolor), f"Versicolor (ID: {int(row_versicolor['_RowID'])})")
add_radar(ax2, norm_values(row_virginica),  f"Virginica (ID: {int(row_virginica['_RowID'])})")
ax2.set_thetagrids(np.degrees(angles[:-1]), labels_feat)
ax2.set_title("Radar Chart")
ax2.legend(loc="upper right", bbox_to_anchor=(1.35, 1.05))
plt.tight_layout()

# ---- 3) Scatterplot matrix (colored by species) ----
color_map = {"setosa": "#1f77b4", "versicolor": "#ff7f0e", "virginica": "#2ca02c"}
colors = df[species_col].map(color_map).values
axes = scatter_matrix(df[feature_cols], figsize=(8, 8), diagonal="kde", color=colors, alpha=0.8)

plt.suptitle("Scatterplot Matrix of Iris (Colored by Species)", y=1.02)
handles = [plt.Line2D([], [], marker="o", linestyle="None", markersize=6, color=c, label=lab.capitalize())
           for lab, c in color_map.items()]
plt.legend(handles=handles, bbox_to_anchor=(1.05, 1), loc="upper left", title="Species")

# 调整画布边距，右边留出空间
plt.tight_layout(rect=[0, 0, 0.85, 0.95])   # rect 调整顶部和右侧空间
plt.show()

