#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
多元统计分析 —— 实习 1
作业：学号 19 → 19 % 4 = 3 → 计算维吉尼亚鸢尾（virginica）
功能：读取 iris.csv → 筛选 virginica → 打印均值向量、协方差矩阵、相关系数矩阵
要求：不保存文件，只打印结果
"""

import os
import numpy as np
import pandas as pd

# -------- 1) 读取数据（按你给的 r'…' 写法 + 兼容 \ 空格） --------
path_raw = r"/Users/jia/Desktop/学习\ /多元统计分析/实验1/Iris数据集/iris.csv"
csv_path = path_raw if os.path.exists(path_raw) else path_raw.replace(r"\ ", " ")

df = pd.read_csv(csv_path, encoding="utf-8")

# -------- 2) 列名与类别标准化 --------
# 找到物种列（不区分大小写）
species_col = None
for c in df.columns:
    if c.lower() == "species":
        species_col = c
        break
if species_col is None:
    raise ValueError("未找到物种列（Species）。请检查 CSV 列名。")

# 可能存在中文类别名 → 映射为英文
mapping = {"山鸢尾": "setosa", "变色鸢尾": "versicolor", "维吉尼亚鸢尾": "virginica"}
df["_Species_std"] = df[species_col].replace(mapping).astype(str).str.lower()

# 只保留数值列（通常是 4 列）
num_cols = [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])]
if len(num_cols) < 2:
    raise ValueError("未检测到足够的数值列，请检查数据。")

# -------- 3) 按学号规则筛选目标物种：virginica --------
target_species = "virginica"
sub = df.loc[df["_Species_std"] == target_species, num_cols].dropna()
if sub.empty:
    raise ValueError("未筛选到 'virginica' 的样本，请检查数据的物种取值。")

# -------- 4) 计算 --------
mean_vec = sub.mean()                 # 均值向量
cov_mat  = sub.cov()                  # 样本协方差（N-1）
corr_mat = sub.ccorr() if hasattr(sub, "ccorr") else sub.corr(method="pearson")  # 兼容旧版本

# -------- 5) 打印（按作业纸格式，保留四位小数） --------
np.set_printoptions(precision=4, suppress=True, floatmode="fixed")
pd.options.display.float_format = lambda x: f"{x:.4f}"

print("多元统计分析 —— 实习 1\n")
print("1. 均值向量")
# 以 (a,b,c,d) 的形式打印
mean_tuple_str = "(" + ",".join(f"{v:.4f}" for v in mean_vec.values) + ")"
print(f"维吉尼亚鸢尾数据的均值向量 {mean_tuple_str}\n")

print("2. 协方差矩阵")
print(np.array(cov_mat.values, dtype=float))
print()  # 空行

print("3. 相关系数矩阵")
print(np.array(corr_mat.values, dtype=float))
