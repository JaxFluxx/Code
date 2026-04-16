# -*- coding: utf-8 -*-
import io
import pandas as pd
import numpy as np
import statsmodels.api as sm
import matplotlib.pyplot as plt

# ========== 1) 读取数据（题目整表；注意这里每行有一个“序号”列） ==========
raw = """Sepal.Length\tSepal.Width\tPetal.Length\tPetal.Width\tSpecies
1\t5.1\t3.5\t1.4\t0.2\tsetosa
2\t4.9\t3\t1.4\t0.2\tsetosa
3\t4.7\t3.2\t1.3\t0.2\tsetosa
4\t4.6\t3.1\t1.5\t0.2\tsetosa
5\t5\t3.6\t1.4\t0.2\tsetosa
6\t5.4\t3.9\t1.7\t0.4\tsetosa
7\t4.6\t3.4\t1.4\t0.3\tsetosa
8\t5\t3.4\t1.5\t0.2\tsetosa
9\t4.4\t2.9\t1.4\t0.2\tsetosa
10\t4.9\t3.1\t1.5\t0.1\tsetosa
11\t5.4\t3.7\t1.5\t0.2\tsetosa
12\t4.8\t3.4\t1.6\t0.2\tsetosa
13\t4.8\t3\t1.4\t0.1\tsetosa
14\t4.3\t3\t1.1\t0.1\tsetosa
15\t5.8\t4\t1.2\t0.2\tsetosa
16\t5.7\t4.4\t1.5\t0.4\tsetosa
17\t5.4\t3.9\t1.3\t0.4\tsetosa
18\t5.1\t3.5\t1.4\t0.3\tsetosa
19\t5.7\t3.8\t1.7\t0.3\tsetosa
20\t5.1\t3.8\t1.5\t0.3\tsetosa
21\t5.4\t3.4\t1.7\t0.2\tsetosa
22\t5.1\t3.7\t1.5\t0.4\tsetosa
23\t4.6\t3.6\t1\t0.2\tsetosa
24\t5.1\t3.3\t1.7\t0.5\tsetosa
25\t4.8\t3.4\t1.9\t0.2\tsetosa
26\t5\t3\t1.6\t0.2\tsetosa
27\t5\t3.4\t1.6\t0.4\tsetosa
28\t5.2\t3.5\t1.5\t0.2\tsetosa
29\t5.2\t3.4\t1.4\t0.2\tsetosa
30\t4.7\t3.2\t1.6\t0.2\tsetosa
31\t4.8\t3.1\t1.6\t0.2\tsetosa
32\t5.4\t3.4\t1.5\t0.4\tsetosa
33\t5.2\t4.1\t1.5\t0.1\tsetosa
34\t5.5\t4.2\t1.4\t0.2\tsetosa
35\t4.9\t3.1\t1.5\t0.2\tsetosa
36\t5\t3.2\t1.2\t0.2\tsetosa
37\t5.5\t3.5\t1.3\t0.2\tsetosa
38\t4.9\t3.6\t1.4\t0.1\tsetosa
39\t4.4\t3\t1.3\t0.2\tsetosa
40\t5.1\t3.4\t1.5\t0.2\tsetosa
41\t5\t3.5\t1.3\t0.3\tsetosa
42\t4.5\t2.3\t1.3\t0.3\tsetosa
43\t4.4\t3.2\t1.3\t0.2\tsetosa
44\t5\t3.5\t1.6\t0.6\tsetosa
45\t5.1\t3.8\t1.9\t0.4\tsetosa
46\t4.8\t3\t1.4\t0.3\tsetosa
47\t5.1\t3.8\t1.6\t0.2\tsetosa
48\t4.6\t3.2\t1.4\t0.2\tsetosa
49\t5.3\t3.7\t1.5\t0.2\tsetosa
50\t5\t3.3\t1.4\t0.2\tsetosa
51\t7\t3.2\t4.7\t1.4\tversicolor
52\t6.4\t3.2\t4.5\t1.5\tversicolor
53\t6.9\t3.1\t4.9\t1.5\tversicolor
54\t5.5\t2.3\t4\t1.3\tversicolor
55\t6.5\t2.8\t4.6\t1.5\tversicolor
56\t5.7\t2.8\t4.5\t1.3\tversicolor
57\t6.3\t3.3\t4.7\t1.6\tversicolor
58\t4.9\t2.4\t3.3\t1\tversicolor
59\t6.6\t2.9\t4.6\t1.3\tversicolor
60\t5.2\t2.7\t3.9\t1.4\tversicolor
61\t5\t2\t3.5\t1\tversicolor
62\t5.9\t3\t4.2\t1.5\tversicolor
63\t6\t2.2\t4\t1\tversicolor
64\t6.1\t2.9\t4.7\t1.4\tversicolor
65\t5.6\t2.9\t3.6\t1.3\tversicolor
66\t6.7\t3.1\t4.4\t1.4\tversicolor
67\t5.6\t3\t4.5\t1.5\tversicolor
68\t5.8\t2.7\t4.1\t1\tversicolor
69\t6.2\t2.2\t4.5\t1.5\tversicolor
70\t5.6\t2.5\t3.9\t1.1\tversicolor
71\t5.9\t3.2\t4.8\t1.8\tversicolor
72\t6.1\t2.8\t4\t1.3\tversicolor
73\t6.3\t2.5\t4.9\t1.5\tversicolor
74\t6.1\t2.8\t4.7\t1.2\tversicolor
75\t6.4\t2.9\t4.3\t1.3\tversicolor
76\t6.6\t3\t4.4\t1.4\tversicolor
77\t6.8\t2.8\t4.8\t1.4\tversicolor
78\t6.7\t3\t5\t1.7\tversicolor
79\t6\t2.9\t4.5\t1.5\tversicolor
80\t5.7\t2.6\t3.5\t1\tversicolor
81\t5.5\t2.4\t3.8\t1.1\tversicolor
82\t5.5\t2.4\t3.7\t1\tversicolor
83\t5.8\t2.7\t3.9\t1.2\tversicolor
84\t6\t2.7\t5.1\t1.6\tversicolor
85\t5.4\t3\t4.5\t1.5\tversicolor
86\t6\t3.4\t4.5\t1.6\tversicolor
87\t6.7\t3.1\t4.7\t1.5\tversicolor
88\t6.3\t2.3\t4.4\t1.3\tversicolor
89\t5.6\t3\t4.1\t1.3\tversicolor
90\t5.5\t2.5\t4\t1.3\tversicolor
91\t5.5\t2.6\t4.4\t1.2\tversicolor
92\t6.1\t3\t4.6\t1.4\tversicolor
93\t5.8\t2.6\t4\t1.2\tversicolor
94\t5\t2.3\t3.3\t1\tversicolor
95\t5.6\t2.7\t4.2\t1.3\tversicolor
96\t5.7\t3\t4.2\t1.2\tversicolor
97\t5.7\t2.9\t4.2\t1.3\tversicolor
98\t6.2\t2.9\t4.3\t1.3\tversicolor
99\t5.1\t2.5\t3\t1.1\tversicolor
100\t5.7\t2.8\t4.1\t1.3\tversicolor
101\t6.3\t3.3\t6\t2.5\tvirginica
102\t5.8\t2.7\t5.1\t1.9\tvirginica
103\t7.1\t3\t5.9\t2.1\tvirginica
104\t6.3\t2.9\t5.6\t1.8\tvirginica
105\t6.5\t3\t5.8\t2.2\tvirginica
106\t7.6\t3\t6.6\t2.1\tvirginica
107\t4.9\t2.5\t4.5\t1.7\tvirginica
108\t7.3\t2.9\t6.3\t1.8\tvirginica
109\t6.7\t2.5\t5.8\t1.8\tvirginica
110\t7.2\t3.6\t6.1\t2.5\tvirginica
111\t6.5\t3.2\t5.1\t2\tvirginica
112\t6.4\t2.7\t5.3\t1.9\tvirginica
113\t6.8\t3\t5.5\t2.1\tvirginica
114\t5.7\t2.5\t5\t2\tvirginica
115\t5.8\t2.8\t5.1\t2.4\tvirginica
116\t6.4\t3.2\t5.3\t2.3\tvirginica
117\t6.5\t3\t5.5\t1.8\tvirginica
118\t7.7\t3.8\t6.7\t2.2\tvirginica
119\t7.7\t2.6\t6.9\t2.3\tvirginica
120\t6\t2.2\t5\t1.5\tvirginica
121\t6.9\t3.2\t5.7\t2.3\tvirginica
122\t5.6\t2.8\t4.9\t2\tvirginica
123\t7.7\t2.8\t6.7\t2\tvirginica
124\t6.3\t2.7\t4.9\t1.8\tvirginica
125\t6.7\t3.3\t5.7\t2.1\tvirginica
126\t7.2\t3.2\t6\t1.8\tvirginica
127\t6.2\t2.8\t4.8\t1.8\tvirginica
128\t6.1\t3\t4.9\t1.8\tvirginica
129\t6.4\t2.8\t5.6\t2.1\tvirginica
130\t7.2\t3\t5.8\t1.6\tvirginica
131\t7.4\t2.8\t6.1\t1.9\tvirginica
132\t7.9\t3.8\t6.4\t2\tvirginica
133\t6.4\t2.8\t5.6\t2.2\tvirginica
134\t6.3\t2.8\t5.1\t1.5\tvirginica
135\t6.1\t2.6\t5.6\t1.4\tvirginica
136\t7.7\t3\t6.1\t2.3\tvirginica
137\t6.3\t3.4\t5.6\t2.4\tvirginica
138\t6.4\t3.1\t5.5\t1.8\tvirginica
139\t6\t3\t4.8\t1.8\tvirginica
140\t6.9\t3.1\t5.4\t2.1\tvirginica
141\t6.7\t3.1\t5.6\t2.4\tvirginica
142\t6.9\t3.1\t5.1\t2.3\tvirginica
143\t5.8\t2.7\t5.1\t1.9\tvirginica
144\t6.8\t3.2\t5.9\t2.3\tvirginica
145\t6.7\t3.3\t5.7\t2.5\tvirginica
146\t6.7\t3\t5.2\t2.3\tvirginica
147\t6.3\t2.5\t5\t1.9\tvirginica
148\t6.5\t3\t5.2\t2\tvirginica
149\t6.2\t3.4\t5.4\t2.3\tvirginica
150\t5.9\t3\t5.1\t1.8\tvirginica
"""


# 用 header=None 读取，再自己命名 6 列
df = pd.read_csv(
    io.StringIO(raw),
    sep="\t",
    header=None,
    names=["id", "Sepal.Length", "Sepal.Width", "Petal.Length", "Petal.Width", "Species"]
)

# 丢弃序号列，数值列转为浮点，去掉可能的缺失
df = df.drop(columns="id")
for col in ["Sepal.Length", "Sepal.Width", "Petal.Length", "Petal.Width"]:
    df[col] = pd.to_numeric(df[col], errors="coerce")
df = df.dropna(subset=["Sepal.Length", "Sepal.Width", "Petal.Length", "Petal.Width"])

y = df["Petal.Length"]
candidates = ["Sepal.Length", "Sepal.Width", "Petal.Width"]

# ========== 2) OLS 帮助函数 ==========
def fit_ols(Xcols):
    X = sm.add_constant(df[Xcols], has_constant="add")
    return sm.OLS(y, X).fit()

def sst(arr):
    arr = np.asarray(arr, dtype=float)
    return np.sum((arr - arr.mean())**2)

def decomp(model):
    y_true = np.asarray(model.model.endog, dtype=float)
    y_hat  = np.asarray(model.fittedvalues, dtype=float)
    SST = sst(y_true)
    SSR = np.sum((y_hat - y_true.mean())**2)
    SSE = np.sum((y_true - y_hat)**2)
    n = int(model.nobs)
    p = int(model.df_model)  # 不含常数项的自变量个数
    adjR2 = 1 - (SSE/(n - p - 1)) / (SST/(n - 1))
    return SST, SSR, SSE, float(model.rsquared), float(model.rsquared_adj)

# ========== 3) Univariate regressions ==========
print("=== Univariate regression comparison ===")
for col in candidates:
    m = fit_ols([col])
    SST, SSR, SSE, R2, R2a = decomp(m)
    print(f"[{col}]  R²={R2:.4f}  Adj.R²={R2a:.4f}  | SST={SST:.3f}  SSR={SSR:.3f}  SSE={SSE:.3f}")
    print(f"  Equation: Ŷ = {m.params['const']:.4f} + {m.params[col]:.4f}×{col}")
    # To display full regression table: print(m.summary())

# ========== 4) Multiple regression: forward stepwise (AIC + significance) ==========
selected, remaining = [], candidates.copy()
current_aic = np.inf
print("\n=== Forward stepwise selection (AIC & p<0.05) ===")
while remaining:
    trials = []
    for col in remaining:
        cols = selected + [col]
        m = fit_ols(cols)
        trials.append((m.aic, col, m))
    trials.sort(key=lambda x: x[0])
    best_aic, best_col, best_model = trials[0]
    pvals = best_model.pvalues.drop("const", errors="ignore")
    if (best_aic < current_aic) and all(pvals < 0.05):
        selected.append(best_col)
        remaining.remove(best_col)
        current_aic = best_aic
        print(f"Added {best_col}  →  AIC={best_aic:.3f}, current predictors: {selected}")
    else:
        break

final_model = fit_ols(selected)
print("\n=== Final multiple regression model ===")
print(final_model.summary())

SST, SSR, SSE, R2, R2a = decomp(final_model)
print(f"\nSum of Squares: SST={SST:.3f}, SSR={SSR:.3f}, SSE={SSE:.3f}")
print(f"Goodness of Fit: R²={R2:.6f},  Adj.R²={R2a:.6f}")

# ========== 5) Residual diagnostics ==========
resid  = final_model.resid
fitted = final_model.fittedvalues

plt.figure()
plt.scatter(fitted, resid)
plt.axhline(0, linestyle="--")
plt.xlabel("Fitted Values")
plt.ylabel("Residuals")
plt.title("Residuals vs Fitted (Final Model)")
plt.tight_layout()
plt.savefig("resid_vs_fitted_en.png", dpi=150)

sm.qqplot(resid, line='45')
plt.title("QQ Plot of Residuals (Final Model)")
plt.tight_layout()
plt.savefig("resid_qq_en.png", dpi=150)

print("\nFigures saved: resid_vs_fitted_en.png, resid_qq_en.png")
