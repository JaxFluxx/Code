import numpy as np
import matplotlib.pyplot as plt

plt.rcParams['font.sans-serif'] = ['Arial Unicode MS']


# 设置 delta 的多个值
delta_values = [1, 5, 10, 20]  # 表示“新解比当前解差多少”
temperatures = np.linspace(0.1, 100, 500)  # 避免除0，温度从0.1到100

# 开始画图
plt.figure(figsize=(10, 6))  # 图像大小

# 针对不同 delta 值画多条曲线
for delta in delta_values:
    probs = np.exp(-delta / temperatures)  # 计算每个温度下的接受概率
    plt.plot(temperatures, probs, label=f'Δ = {delta}')  # 绘图并加标签

# 图像样式设置
plt.title('接受概率 $exp(-\\Delta / T)$ 随温度变化曲线')
plt.xlabel('Temperature (T)')
plt.ylabel('Acceptance Probability')
plt.ylim(0, 1.05)  # 限定 y 轴范围
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()
