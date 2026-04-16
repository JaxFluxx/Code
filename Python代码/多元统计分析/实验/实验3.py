#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Experiment 3 — Assess Multivariate Normality on Iris
Rule: student ID = 19 -> 19 % 4 = 3 -> use Setosa (山鸢尾)

What this script does:
1) Read iris.csv (handles the '\ ' in your path)
2) Filter the target group (Setosa)
3) Compute univariate skewness & excess kurtosis for each feature
4) Make Q–Q plots vs Normal for each feature
5) Assess multivariate normality:
   - Mardia’s multivariate skewness (b1p) and kurtosis (b2p) with asymptotic p-values
   - Chi-square Q–Q plot of Mahalanobis distances (multivariate Q–Q)
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import skew, kurtosis, chi2, norm

# --------------------- 0) Read CSV & select group ---------------------
path_raw = r"/Users/jia/Desktop/学习\ /多元统计分析/实验1/Iris数据集/iris.csv"
csv_path = path_raw if os.path.exists(path_raw) else path_raw.replace(r"\ ", " ")
df = pd.read_csv(csv_path, encoding="utf-8")

feature_cols = ["Sepal.Length", "Sepal.Width", "Petal.Length", "Petal.Width"]
species_col = next((c for c in df.columns if c.lower() == "species"), "Species")
assert set(feature_cols).issubset(df.columns), "CSV must contain the 4 numeric Iris columns."

# unify species labels to English
mapping = {"山鸢尾": "setosa", "变色鸢尾": "versicolor", "维吉尼亚鸢尾": "virginica"}
df[species_col] = df[species_col].replace(mapping).str.lower()

# Student ID rule for Experiment 3:
# remainder 1 -> versicolor, 2 -> overall, 3 -> setosa, 0 -> virginica
remainder = 19 % 4
if remainder == 1:
    subset = df[df[species_col] == "versicolor"]
    group_name = "Versicolor"
elif remainder == 2:
    subset = df.copy()
    group_name = "All species (overall)"
elif remainder == 3:
    subset = df[df[species_col] == "setosa"]
    group_name = "Setosa"
else:
    subset = df[df[species_col] == "virginica"]
    group_name = "Virginica"

X = subset[feature_cols].to_numpy(dtype=float)
n, p = X.shape

# --------------------- 1) Univariate skewness & kurtosis ---------------------
# skewness: 0 for normal; kurtosis(excess): 0 for normal (so normal kurtosis = 3, excess=0)
skews = pd.Series(skew(X, axis=0, bias=False), index=feature_cols)
ex_kurt = pd.Series(kurtosis(X, axis=0, fisher=True, bias=False), index=feature_cols)

print("=== Experiment 3: Multivariate Normality Assessment ===")
print(f"Group: {group_name} | n = {n}, p = {p}\n")
print("Univariate skewness (Normal -> 0):")
print(skews.round(4).to_string())
print("\nUnivariate excess kurtosis (Normal -> 0):")
print(ex_kurt.round(4).to_string())
print()

# --------------------- 2) Univariate Q–Q plots vs Normal ---------------------
fig, axes = plt.subplots(2, 2, figsize=(8, 7), dpi=120)
axes = axes.ravel()
for i, col in enumerate(feature_cols):
    ax = axes[i]
    x = X[:, i]
    x = x[~np.isnan(x)]
    x_sorted = np.sort(x)
    n_i = len(x_sorted)
    # Theoretical quantiles for N(0,1)
    probs = (np.arange(1, n_i + 1) - 0.5) / n_i
    q_theory = norm.ppf(probs)
    # Standardize data (z-scores)
    x_std = (x_sorted - x_sorted.mean()) / x_sorted.std(ddof=1)
    ax.scatter(q_theory, x_std, s=18, alpha=0.8)
    # Reference line
    slope = np.std(x_std, ddof=1) / np.std(q_theory, ddof=1)
    intercept = np.mean(x_std) - slope * np.mean(q_theory)
    xx = np.linspace(q_theory.min(), q_theory.max(), 100)
    ax.plot(xx, intercept + slope * xx, lw=2)
    ax.set_title(f"Q–Q: {col}")
    ax.set_xlabel("Theoretical Quantiles (N(0,1))")
    ax.set_ylabel("Standardized Data")
plt.suptitle(f"Univariate Q–Q Plots — {group_name}", y=0.98)
plt.tight_layout(rect=[0, 0, 1, 0.96])

# --------------------- 3) Mardia’s multivariate skewness & kurtosis ---------------------
# Center & covariance
mu = X.mean(axis=0)
S = np.cov(X, rowvar=False, ddof=1)
Sinv = np.linalg.inv(S)

# Mardia's skewness b1p = (1/n^2) * sum_{i,j} [(x_i - mu)' S^{-1} (x_j - mu)]^3
# Efficient computation via G = Z S^{-1} Z^T (Z: n×p centered)
Z = X - mu
G = Z @ Sinv @ Z.T      # n×n
b1p = (1.0 / (n**2)) * np.sum(G**3)

# Approximate test statistic & p-value (Doornik & Hansen / Mardia asymptotics)
# k = p(p+1)(p+2)/6  (number of distinct third-order moments)
k = p * (p + 1) * (p + 2) / 6.0
chi2_stat_skew = n * b1p / 6.0
pval_skew = 1.0 - chi2.cdf(chi2_stat_skew, df=int(k))

# Mardia's kurtosis b2p = (1/n) * sum_i [(x_i - mu)' S^{-1} (x_i - mu)]^2
d2 = np.sum((Z @ Sinv) * Z, axis=1)  # Mahalanobis^2 for each i
b2p = np.mean(d2**2)

# For normal: E[b2p] = p(p+2)
expected_b2p = p * (p + 2)
# Asymptotic variance of b2p under H0: Var(b2p) = 8p(p+2)/n
var_b2p = (8.0 * p * (p + 2)) / n
z_kurt = (b2p - expected_b2p) / np.sqrt(var_b2p)
# Two-sided p-value using Normal(0,1)
from scipy.stats import norm as _norm
pval_kurt = 2.0 * (1.0 - _norm.cdf(abs(z_kurt)))

print("Mardia’s multivariate skewness:")
print(f"  b1p = {b1p:.4f}")
print(f"  Chi-square statistic = {chi2_stat_skew:.4f}, df = {int(k)}, p-value = {pval_skew:.4g}")
print("\nMardia’s multivariate kurtosis:")
print(f"  b2p = {b2p:.4f},  expected under Normal = {expected_b2p:.4f}")
print(f"  Z (asymptotic) = {z_kurt:.4f}, p-value = {pval_kurt:.4g}\n")

# --------------------- 4) Multivariate Q–Q via Mahalanobis^2 vs Chi-square ---------------------
# Sort Mahalanobis distances and compare to chi-square quantiles with df = p
d2_sorted = np.sort(d2)
probs = (np.arange(1, n + 1) - 0.5) / n
chi2_theory = chi2.ppf(probs, df=p)

plt.figure(figsize=(6.8, 5.6), dpi=120)
plt.scatter(chi2_theory, d2_sorted, s=22, alpha=0.85)
# Reference line (fit)
m = np.polyfit(chi2_theory, d2_sorted, 1)
xx = np.linspace(chi2_theory.min(), chi2_theory.max(), 200)
plt.plot(xx, m[0]*xx + m[1], lw=2)
plt.title(f"Multivariate Q–Q (Mahalanobis² vs Chi-square, df={p}) — {group_name}")
plt.xlabel("Theoretical Chi-square Quantiles")
plt.ylabel("Empirical Mahalanobis²")
plt.tight_layout()

plt.show()

# --------------------- 5) Quick interpretation hints (printed) ---------------------
print("Interpretation hints:")
print("- Univariate: skew≈0 and excess kurtosis≈0 suggest normal shape per feature.")
print("- Univariate Q–Q: points close to the line suggest normality for that feature.")
print("- Mardia skewness: small p-value -> reject multivariate normality (skewness too large).")
print("- Mardia kurtosis: small p-value -> reject multivariate normality (kurtosis deviates).")
print("- Multivariate Q–Q: points near reference line suggest a good multivariate Normal fit.")

# ======= 中文输出：第一问（偏度与峰度） =======
feat_zh = ["花萼长度", "花萼宽度", "花瓣长度", "花瓣宽度"]  # 对应 feature_cols 顺序

print("\n" + "=" * 68)
print(f"多元统计分析——实习 3：偏度与峰度（组别：{group_name}）")
print(f"样本量 n = {n}，维度 p = {p}")
print("=" * 68)

# 表头
header = f"{'特征':<8} | {'偏度(Skewness)':>16} | {'超额峰度(Excess)':>18}"
print(header)
print("-" * len(header))

# 表体（保留 6 位小数）
for i, name in enumerate(feat_zh):
    sk = f"{float(skews.iloc[i]):.6f}"
    ku = f"{float(ex_kurt.iloc[i]):.6f}"
    print(f"{name:<8} | {sk:>16} | {ku:>18}")

print("-" * len(header))
print("说明：正态分布的理论值为 偏度≈0，超额峰度≈0；偏离越大，越可能不服从正态。")
print("=" * 68 + "\n")
