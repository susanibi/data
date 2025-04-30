import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm

# Hardcoded parameters
eta0 = 0.9  # baseline viscosity (mPa·s)
k = np.log(1.28 / eta0) / 2.5  # fitted exponent ≈0.141
cmc = 0.403  # critical micelle concentration in % w/v

# Concentration arrays
c_full = np.linspace(0, 10, 400)
c_zoom = np.linspace(0, 1, 200)

# Exponential model calculations
eta_full = eta0 * np.exp(k * c_full)
eta_zoom = eta0 * np.exp(k * c_zoom)

# Color settings using viridis colormap
cmap = cm.get_cmap('viridis')
line_color = cmap(0.6)
point_color = cmap(0.2)

# Full-range plot (0–10%)
plt.figure(figsize=(8, 4))
plt.plot(c_full, eta_full, color=line_color, linewidth=2,
         label=f'η = {eta0}·exp({k:.3f}·c)')
plt.scatter([0, 2.5], [0.9, 1.28], color=point_color, s=60, marker='o',
            label='Liu data: 0.9 → 1.28')
plt.text(6, 3.2, f'k = {k:.3f}', color=line_color, fontsize=12)
plt.title('Exponential Viscosity Model (0–10%)')
plt.xlabel('Pluronic F‑68 Concentration (%)')
plt.ylabel('Viscosity (mPa·s)')
plt.xlim(0, 10)
plt.ylim(0.8, eta_full.max() * 1.05)
plt.legend()
plt.grid(True)

# Zoomed-in plot (0–1%)
plt.figure(figsize=(8, 4))
plt.plot(c_zoom, eta_zoom, color=line_color, linewidth=2,
         label=f'η = {eta0}·exp({k:.3f}·c)')
plt.scatter([0.05], [eta0 * np.exp(k * 0.05)], color=point_color, s=80, marker='X',
            label=f'0.05% → {eta0 * np.exp(k * 0.05):.3f} mPa·s')
plt.axvline(cmc, linestyle='--', color='gray', label=f'CMC ≈ {cmc:.3f}%')
plt.text(0.6, 1.035, f'k = {k:.3f}', color=line_color, fontsize=12)
plt.title('Exponential Model Zoom (0–1%)')
plt.xlabel('Pluronic F‑68 Concentration (%)')
plt.ylabel('Viscosity (mPa·s)')
plt.xlim(0, 1)
plt.ylim(0.88, eta_zoom.max() * 1.05)
plt.legend()
plt.grid(True)

plt.tight_layout()
plt.show()
