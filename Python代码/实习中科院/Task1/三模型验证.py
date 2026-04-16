import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

plt.rcParams['font.sans-serif'] = ['Arial Unicode MS']

# 定义系统可靠性函数 R(t)
def R(t, lam, c):
    return (np.exp(-3*lam*t)
            + 3*c*(np.exp(-2*lam*t) - np.exp(-3*lam*t))
            + 3*c**2*(np.exp(-lam*t) - 2*np.exp(-2*lam*t) + np.exp(-3*lam*t)))

# 参数设定
lambda_list = [1e-6, 5e-7]
c_list = [0.7, 0.8, 0.9]
t_sample = 50000  # 指定采样时间点

# 存储表格数据
table_data = []

# 填表格数据
for lam in lambda_list:
    for c in c_list:
        reliability = R(t_sample, lam, c)
        table_data.append({
            'λ (故障率)': f'{lam:.0e}',
            'c (检测成功率)': c,
            f'R({t_sample})': round(reliability, 6)
        })

# 创建 DataFrame 表格
df = pd.DataFrame(table_data)

# 打印表格
print("三处理器容错系统在 t = {} 时的可靠性（R(t))：\n".format(t_sample))
print(df.to_string(index=False))

# 画图：不同组合下 R(t) 曲线
t = np.linspace(0, 100000, 500)
plt.figure(figsize=(10, 6))

for lam in lambda_list:
    for c in c_list:
        R_values = R(t, lam, c)
        label = f"λ={lam:.0e}, c={c}"
        plt.plot(t, R_values, label=label)

plt.title("System Reliability R(t) for Different λ and c")
plt.xlabel("Time (t)")
plt.ylabel("Reliability R(t)")
plt.ylim(0.9, 1.001)
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()
