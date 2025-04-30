import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm
from statsmodels.formula.api import ols

# Hardcoded data
data = {
    "Cell Conc": [
        "≤40", "≤40", "≤40", "≤40", "≤40", 200, 200, 200, 200, 200, 200,
        300, 300, 300, 300, 300, 300, 300, 300, 300, 300
    ],
    "F68 (%)": [
        0.02, 0.02, 0.05, 0.05, 0.05, 0.01, 0.01, 0.02, 0.02, 0.03, 0.04,
        0.00, 0.00, 0.00, 0.00, 0.01, 0.01, 0.05, 0.05, 0.05, 0.05
    ],
    "RG (%)": [
        0.00, 0.05, 0.15, 0.00, 0.00, 0.00, 0.00, 0.00, 0.01, 0.00, 0.00,
        0.00, 0.00, 0.00, 0.05, 0.00, 0.05, 0.00, 0.00, 0.00, 0.00
    ],
    "Split Eff": [
        97.27, 96.88, 100, 100, 98.44, 0, 9.38, 1.56, 65.23, 9.38, 50,
        0, 0, 0, 10.94, 5, 100, 90.63, 78.13, 93.36, 98.44
    ]
}

df = pd.DataFrame(data)
df["Conc Group"] = df["Cell Conc"]

# Calculate weighted surfactant score (based on regression-derived β₁/β₂ ratio)
weight_ratio = 5.24
df["Weighted Surfactant Score"] = df["F68 (%)"] * weight_ratio + df["RG (%)"]

# Define groups with consistent data types (note the numbers are not quoted)
groups = ["≤40", 200, 300]
zlim = (0, 110)

fig = plt.figure(figsize=(18, 6))

for i, group in enumerate(groups, start=1):
    subset = df[df["Conc Group"] == group]

    # Safeguard: Check if the subset is empty
    if subset.empty:
        print(f"Warning: No data for group {group}")
        continue

    f68_vals = np.linspace(subset["F68 (%)"].min(), subset["F68 (%)"].max(), 30)
    rg_vals = np.linspace(subset["RG (%)"].min(), subset["RG (%)"].max(), 30)
    f68_grid, rg_grid = np.meshgrid(f68_vals, rg_vals)
    score_grid = f68_grid * weight_ratio + rg_grid

    model = ols("Q('Split Eff') ~ Q('Weighted Surfactant Score')", data=subset).fit()
    grid_df = pd.DataFrame({
        "Weighted Surfactant Score": score_grid.ravel()
    })
    grid_df["Predicted Split"] = model.predict(grid_df).clip(lower=0, upper=110)
    z_grid = grid_df["Predicted Split"].values.reshape(f68_grid.shape)

    ax = fig.add_subplot(1, 3, i, projection='3d')
    surf = ax.plot_surface(f68_grid, rg_grid, z_grid, cmap=cm.viridis, alpha=0.85)

    ax.scatter(
        subset["F68 (%)"], subset["RG (%)"], subset["Split Eff"],
        color='black', edgecolor='black', s=50, depthshade=False
    )

    ax.set_xlabel("F68 (%)", fontsize=12)
    ax.set_ylabel("RG (%)", fontsize=12)
    ax.set_zlabel("Split Efficiency (%)", fontsize=12)
    ax.set_zlim(zlim)
    ax.set_title(f"Cell Conc = {group}", fontsize=12)
    ax.tick_params(labelsize=8)
    ax.view_init(elev=25, azim=230)

plt.subplots_adjust(left=0.05, right=0.82)
cbar_ax = fig.add_axes([0.84, 0.15, 0.02, 0.7])
fig.colorbar(surf, cax=cbar_ax, label="Predicted Split Efficiency")

# Save the output
plt.savefig("3D_Surface_Plots_WeightedScore_Hardcoded.png", dpi=300, bbox_inches='tight')
plt.show()
