# roofline_schematic.py
# 简易 Roofline 示意图（形状示意，非实测）

import numpy as np
import matplotlib.pyplot as plt

plt.rcParams['font.sans-serif'] = ['Arial Unicode MS']

# ===== 可调占位参数（仅用于画图形状） =====
C_HW = 100.0    # 计算上限（TFLOPS）示意
B_EFF = 20.0    # 有效带宽（GB/s）示意
# =====================================

# OI 从 0.1 到 1000（对数轴更好地展示“斜线+平台”）
OI = np.logspace(-1, 3, 400)  # FLOP/Byte
C_band = B_EFF * OI           # 带宽上限折算的算力
C_task = np.minimum(C_band, C_HW)  # Roofline: min(C_hw, B_eff * OI)

# 拐点（knee）：当 B_eff * OI = C_hw
OI_knee = C_HW / B_EFF

plt.figure(figsize=(7, 4.5))
# 画可交付算力曲线（粗线）
plt.loglog(OI, C_task, linewidth=2.5, label=r"$C_{\mathrm{task}}=\min(C_{\mathrm{hw}},\,B_{\mathrm{eff}}\cdot OI)$")

# 参考线：带宽上限斜线 & 计算上限水平线（虚线）
plt.loglog(OI, C_band, linestyle="--", linewidth=1.5, label=r"带宽上限 $B_{\mathrm{eff}}\cdot OI$")
plt.axhline(C_HW, linestyle="--", linewidth=1.5, label=r"计算上限 $C_{\mathrm{hw}}$")

# 拐点标注（虚线辅助）
plt.axvline(OI_knee, linestyle=":", linewidth=1.0)
plt.scatter([OI_knee], [C_HW], s=30)
plt.text(OI_knee*1.1, C_HW*1.05, "拐点", va="bottom")

# 轴与标题
plt.xlabel(r"运算强度 $OI$ (FLOP/Byte)")
plt.ylabel(r"可交付算力 $C_{\mathrm{task}}$ (TFLOPS)")
plt.title(" Roofline 示意图")

# 注释：带宽受限区 / 计算受限区（大致区域标示）
# 只做文本提示，不绘制额外形状，避免喧宾夺主
plt.text(OI[5], (B_EFF*OI[5])*1.3, "带宽受限区\n(斜率 ≈ B_eff)", ha="left", va="bottom")
plt.text(OI[-80], C_HW*0.7, "计算受限区\n(平台 ≈ C_hw)", ha="right", va="center")

plt.grid(True, which="both", linewidth=0.6, alpha=0.3)
plt.legend(loc="lower right", frameon=False)
plt.tight_layout()
plt.savefig("roofline_schematic.png", dpi=200, bbox_inches="tight")
plt.show()

# 使用说明：
# 1) 直接运行：python roofline_schematic.py
# 2) 若想调整拐点位置：改 C_HW 或 B_EFF（拐点 OI_knee = C_HW / B_EFF）
