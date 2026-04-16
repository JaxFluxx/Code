import numpy as np
import matplotlib.pyplot as plt

# -----------------------------
# Parameters (edit as you like)
# -----------------------------
C_hw   = 100.0   # Compute ceiling, in TFLOPS
B_eff  = 10.0    # Effective memory bandwidth, in TBytes/s
x_min, x_max = 1e-1, 1e3  # OI range (FLOP/Byte)

# Ridge point where B_eff * OI = C_hw
oi_star = C_hw / B_eff
y_star  = C_hw

# -----------------------------
# Curves
# -----------------------------
OI = np.logspace(np.log10(x_min), np.log10(x_max), 1000)
bandwidth_ceiling = B_eff * OI
C_task = np.minimum(C_hw, bandwidth_ceiling)

# -----------------------------
# Plot
# -----------------------------
fig, ax = plt.subplots(figsize=(9, 6), dpi=140)

# Main curves
ax.plot(OI, C_task, lw=3, label=r"$C_{\rm task}=\min(C_{\rm hw},\, B_{\rm eff}\cdot OI)$")
ax.plot(OI, bandwidth_ceiling, ls="--", lw=2, label=r"Bandwidth ceiling $B_{\rm eff}\cdot OI$")
ax.hlines(C_hw, x_min, x_max, ls="--", lw=2, label=r"Compute ceiling $C_{\rm hw}$")

# Ridge point & guides
ax.vlines(oi_star, ax.get_ylim()[0], y_star, ls=":", lw=1.8)
ax.hlines(y_star, x_min, oi_star, ls=":", lw=1.8)
ax.scatter([oi_star], [y_star], s=30, zorder=5)
ax.text(oi_star*1.07, y_star*1.12, "Ridge point", fontsize=10)

# Region annotations
ax.text(0.13, 0.17, "Bandwidth-bound region\n(slope ≈ B_eff)", transform=ax.transAxes,
        ha="left", va="center")
ax.text(0.59, 0.58, "Compute-bound region\n(plateau ≈ C_hw)", transform=ax.transAxes,
        ha="left", va="center")

# Axes format
ax.set_xscale("log")
ax.set_yscale("log")
ax.set_xlim(x_min, x_max)
# Set a y-range that shows the main features clearly
ax.set_ylim(3, 3e3)

ax.set_title("Roofline Diagram (Illustration)", fontsize=13, pad=10)
ax.set_xlabel("Operational Intensity  OI  (FLOP/Byte)")
ax.set_ylabel("Deliverable Compute  $C_{\\rm task}$  (TFLOPS)")

ax.grid(True, which="both", ls=":", lw=0.8, alpha=0.7)
ax.legend(loc="lower right", frameon=False)

plt.tight_layout()
plt.show()
