import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

def f_T(T):
    T = np.asarray(T, dtype=float)
    f = np.empty_like(T)

    mask1 = T <= 80
    f[mask1] = 1.0

    mask2 = (T > 80) & (T <= 90)
    f[mask2] = 1.0 - 0.01*(T[mask2] - 80)

    mask3 = (T > 90) & (T <= 95)
    f[mask3] = 0.90 - 0.02*(T[mask3] - 90)

    mask4 = T > 95
    f[mask4] = 0.80
    return f

T = np.linspace(60, 100, 801)
y = f_T(T)

key_pts = [(80, 1.00), (90, f_T(90)), (95, f_T(95))]

fig, ax = plt.subplots(figsize=(10, 6), dpi=140)

# main curve
ax.plot(T, y, lw=3, zorder=3)
# markers (keep, but no % labels)
for x, yv in key_pts:
    ax.scatter(x, yv, color="crimson", s=40, zorder=5)

# guidelines (keep)
ax.hlines([1.0, 0.80], xmin=60, xmax=100, colors="gray", linestyles=":", linewidth=1)
for x, ls, c in [(80, "--", "seagreen"), (90, "--", "orange"), (95, "--", "firebrick")]:
    ax.vlines(x, 0.76, 1.03, colors=c, linestyles=ls, linewidth=1.5, zorder=1)

# unified corner note (top-right)
corner_text = "Trigger: 80°C\nAccelerated point: 90°C\nHard cap: 95°C"
ax.text(
    0.98, 0.98, corner_text,
    transform=ax.transAxes, ha="right", va="top", fontsize=10,
    bbox=dict(boxstyle="round", facecolor="white", alpha=0.9, edgecolor="gray")
)

# region boxes + captions
ax.add_patch(Rectangle((60, 0.76), 20, 0.27, facecolor="#c8e6c9", alpha=0.35, ec="none"))
ax.text(70, 0.90, "Safe zone\n(T ≤ 80°C)\nNo derating", ha="center", va="center")

ax.add_patch(Rectangle((80, 0.76), 10, 0.27, facecolor="#fff3cd", alpha=0.60, ec="none"))
ax.text(85, 0.90, "Warning zone\n(80–90°C)\n−1% per °C", ha="center", va="center")

ax.add_patch(Rectangle((90, 0.76), 5, 0.27, facecolor="#ffe0b2", alpha=0.7, ec="none"))
ax.text(92.5, 0.90, "Risk zone\n(90–95°C)\n−2% per °C", ha="center", va="center")

ax.add_patch(Rectangle((95, 0.76), 5, 0.27, facecolor="#f8d7da", alpha=0.65, ec="none"))
ax.text(97.5, 0.90, "Critical zone\n(T > 95°C)\nCapped at 80%", ha="center", va="center")

# axes
ax.set_title("Temperature Derating Factor  f(T)", fontsize=14, pad=8)
ax.set_xlabel("Temperature (°C)")
ax.set_ylabel("Derating Factor")
ax.set_xlim(60, 100)
ax.set_ylim(0.76, 1.03)
ax.set_xticks(np.arange(60, 101, 5))
ax.set_yticks(np.arange(0.80, 1.01, 0.05))
ax.grid(True, linestyle=":", linewidth=0.8, alpha=0.7)

plt.tight_layout()
plt.show()
