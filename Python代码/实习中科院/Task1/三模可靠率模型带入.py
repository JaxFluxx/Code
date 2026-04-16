import numpy as np
from scipy.linalg import expm
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter

plt.rcParams['font.sans-serif'] = ['Arial Unicode MS']

# 初始状态向量（12个状态 + terminal）
p0 = np.zeros(13)
p0[0] = 1  # State00 初始为1，其余为0

# 定义函数计算任意时刻的状态概率分布
def state_probabilities_CPU(t, λC, λC_star, μC, μAW, λAW):
    G = np.array([
        [-(3*λC + 3*λC_star + λAW), 3*λC, 3*λC_star, 0, 0, 0, λAW, 0, 0, 0, 0, 0, 0],
        [μC, -(μC + 2*λC + 3*λC_star + λAW), λC_star, 2*λC, 0, 2*λC_star, 0, λAW, 0, 0, 0, 0, 0],
        [0, 0, -(2*λC + 2*λC_star + λAW), 0, 2*λC_star, 2*λC, 0, 0, λAW, 0, 0, 0, 0],
        [0, 2*μC, 0, -(2*μC + 3*λC_star + λC + λAW), 0, 2*λC_star, 0, 0, 0, λAW, 0, 0, λC + λC_star],
        [0, 0, 0, 0, -(λAW + λC + λC_star), 0, 0, 0, 0, 0, λAW, 0, λC + λC_star],
        [0, 0, μC, 0, λC_star, -(μC + λC + 2*λC_star + λAW), 0, 0, 0, 0, 0, λAW, λC + λC_star],
        [μAW, 0, 0, 0, 0, 0, -(μAW + 3*λC + 3*λC_star), 3*λC, 3*λC_star, 0, 0, 0, 0],
        [0, μAW, 0, 0, 0, 0, μC, -(μC + μAW + 2*λC + 3*λC_star), λC_star, 2*λC, 0, 2*λC_star, 0],
        [0, 0, μAW, 0, 0, 0, 0, 0, -(2*λC + 2*λC_star + μAW), 0, 2*λC_star, 2*λC, 0],
        [0, 0, 0, μAW, 0, 0, 0, 2*μC, 0, -(2*μC + μAW + 3*λC_star + λC), 0, 2*λC_star, λC + λC_star],
        [0, 0, 0, 0, μAW, 0, 0, 0, 0, 0, -(μAW + λC + λC_star), 0, λC + λC_star],
        [0, 0, 0, 0, 0, μAW, 0, λC, 0, λC_star, 0, -(μAW + 2*λC + 2*λC_star), λC + λC_star],
        [0]*13
    ])
    return p0 @ expm(G * t)

# 设定参数并计算 t=100 时状态概率
λC = 0.01
λC_star = 0.001
μC = 0.1
λAW = 3 * λC**2 - 2 * λC**3
μAW = 0.2
t = 100

probabilities = state_probabilities_CPU(t, λC, λC_star, μC, μAW, λAW)
R_cpu = np.sum(probabilities[:12])
failure = probabilities[12]

print("At time t =", t)
print("State Probabilities =", probabilities)
print("Reliability R_cpu(t) =", R_cpu)
print("Failure Probability =", failure)


###########################################################################
# 时间范围
t_values = np.linspace(0, 150, 100)
reliabilities = []

# 计算每个时刻的系统可靠性
for t in t_values:
    probs = state_probabilities_CPU(t, λC, λC_star, μC, μAW, λAW)
    reliability = np.sum(probs[:12])
    reliabilities.append(reliability)

# 绘图
plt.figure(figsize=(10, 6))
plt.plot(t_values, reliabilities, label="系统正常运行&降级运行", color='orange', linewidth=2)
plt.title("可靠性图", fontsize=14)
plt.xlabel("时间（天）", fontsize=12)
plt.ylabel("可靠性 (%)", fontsize=12)
plt.grid(True)
plt.xlim(0, 150)
plt.ylim(0.75, 1.01)

# 设置Y轴为百分比格式
plt.gca().yaxis.set_major_formatter(PercentFormatter(xmax=1.0, decimals=0))

# 添加Y轴每隔5%横虚线
for y in np.arange(0.60, 1.01, 0.05):
    plt.axhline(y=y, linestyle='--', color='gray', linewidth=0.5)

# 添加X轴每隔10天竖虚线，并标注交点
for x in np.arange(0, 151, 10):
    plt.axvline(x=x, linestyle='--', color='gray', linewidth=0.5)
    p = state_probabilities_CPU(x, λC, λC_star, μC, μAW, λAW)
    r = np.sum(p[:12])
    # 标注可靠度
    plt.text(x + 0.3, r + 0.002, f"{r*100:.1f}%", fontsize=8, color='blue')
    # 添加红色点
    plt.plot(x, r, 'ro')  # 红色圆点

# ---------- 新版：绘制正常运行概率（使用左侧Y轴 + 实线 + 点 + 标注） ----------
# 计算每个时刻的正常运行概率（State00, 01, 02）
normal_probs = []
for t in t_values:
    probs = state_probabilities_CPU(t, λC, λC_star, μC, μAW, λAW)
    normal = probs[0] + probs[1] + probs[2]
    normal_probs.append(normal)

# 绘制绿色实线曲线（共用左侧Y轴）
plt.plot(t_values, normal_probs, label="系统正常运行", color='green', linestyle='-', linewidth=2)

# 添加X轴每隔10天的绿线红点与标注
for x in np.arange(0, 151, 10):
    p = state_probabilities_CPU(x, λC, λC_star, μC, μAW, λAW)
    normal = p[0] + p[1] + p[2]
    # 添加红点
    plt.plot(x, normal, 'ro')
    # 添加蓝色标注
    plt.text(x + 0.3, normal + 0.002, f"{normal*100:.1f}%", fontsize=8, color='blue')

# 修改图例位置为右上角，自动合并橙线和绿线图例
plt.legend(loc='upper right')


plt.legend()
plt.tight_layout()
plt.show()
