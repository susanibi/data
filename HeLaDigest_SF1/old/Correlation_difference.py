import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from tkinter import Tk, filedialog
from scipy.stats import spearmanr

def main():
    # File picker
    root = Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(title="Select CSV file")
    if not file_path:
        print("❌ No file selected.")
        return

    # Load and clean data
    df = pd.read_csv(file_path)
    x_gravy = pd.to_numeric(df["GRAVY_bin"], errors="coerce").to_numpy()
    diff = pd.to_numeric(df["Difference"], errors="coerce").to_numpy()
    sem0 = pd.to_numeric(df["Combined_SEM0"], errors="coerce").to_numpy()
    x_mean = pd.to_numeric(df["3p2_Mean"], errors="coerce").to_numpy()
    y_mean = pd.to_numeric(df["3p5_Mean"], errors="coerce").to_numpy()
    sem_x = pd.to_numeric(df["3p2_SEM"], errors="coerce").to_numpy()
    sem_y = pd.to_numeric(df["3p5_SEM"], errors="coerce").to_numpy()

    # Clean and sort
    valid = ~np.isnan(x_gravy) & ~np.isnan(diff) & ~np.isnan(sem0) & \
            ~np.isnan(x_mean) & ~np.isnan(y_mean) & ~np.isnan(sem_x) & ~np.isnan(sem_y)

    x_gravy = x_gravy[valid]
    diff = diff[valid]
    sem0 = sem0[valid]
    x_mean = x_mean[valid]
    y_mean = y_mean[valid]
    sem_x = sem_x[valid]
    sem_y = sem_y[valid]

    idx_sorted = np.argsort(x_gravy)
    x_gravy = x_gravy[idx_sorted]
    diff = diff[idx_sorted]
    sem0 = sem0[idx_sorted]
    x_mean = x_mean[idx_sorted]
    y_mean = y_mean[idx_sorted]
    sem_x = sem_x[idx_sorted]
    sem_y = sem_y[idx_sorted]

    # Correlations
    r1, p1 = spearmanr(x_mean, y_mean)
    r2, p2 = spearmanr(x_gravy, diff)
    print(f"🔹 3p2 vs 3p5 mean: r = {r1:.4f}, p = {p1:.3e}")
    print(f"🔸 GRAVY vs difference: r = {r2:.4f}, p = {p2:.3e}")

    # Highlighted bins
    highlight_bins = [-2.75, -2.05, 1.20, 1.65]
    highlight_indices = [np.argmin(np.abs(x_gravy - val)) for val in highlight_bins]

    # GRAVY colormap
    cmap = plt.get_cmap("viridis")
    norm = plt.Normalize(x_gravy.min(), x_gravy.max())
    colors = cmap(norm(x_gravy))

    # --- Plot 1: 3p2 vs 3p5 ---
    fig1, ax1 = plt.subplots(figsize=(8, 6))
    for xi, yi, xe, ye in zip(x_mean, y_mean, sem_x, sem_y):
        ax1.fill_betweenx([yi - ye, yi + ye], xi - xe, xi + xe, color='lightblue', alpha=0.3)
    ax1.scatter(x_mean, y_mean, color='steelblue', alpha=0.8)

    for idx in highlight_indices:
        ax1.plot(x_mean[idx], y_mean[idx], 'o', markersize=10, markeredgecolor='darkred',
                 markerfacecolor='none', linewidth=2)
        ax1.text(x_mean[idx], y_mean[idx], f'{x_gravy[idx]:.2f}', color='darkred', fontsize=8)

    lims = [min(x_mean.min(), y_mean.min()), max(x_mean.max(), y_mean.max())]
    ax1.plot(lims, lims, '--', color='gray')
    ax1.set_title(f"Correlation: 3p2 vs 3p5\nSpearman r = {r1:.2f}, p = {p1:.2e}")
    ax1.set_xlabel("3p2_50pg_ACN (Mean Abundance)")
    ax1.set_ylabel("3p5_50pg_ACN (Mean Abundance)")
    ax1.grid(True)
    fig1.tight_layout()

    # --- Plot 2: GRAVY vs Difference ---
    fig2, ax2 = plt.subplots(figsize=(10, 6))
    ax2.fill_between(x_gravy, diff - sem0, diff + sem0, alpha=0.3, color='lightgray')
    for xi, yi, ci in zip(x_gravy, diff, colors):
        ax2.plot(xi, yi, marker='o', color=ci)
    ax2.plot(x_gravy, diff, color='gray', alpha=0.4)

    for idx in highlight_indices:
        ax2.plot(x_gravy[idx], diff[idx], 'o', markersize=10, markeredgecolor='darkred',
                 markerfacecolor='none', linewidth=2)
        ax2.text(x_gravy[idx], diff[idx], f'{x_gravy[idx]:.2f}', color='darkred', fontsize=8)

    ax2.axhline(0, color='gray', linestyle='--')
    ax2.set_title(f"GRAVY Bin vs Difference (3p2 - 3p5)\nSpearman r = {r2:.2f}, p = {p2:.2e}")
    ax2.set_xlabel("GRAVY Bin Lower Bound")
    ax2.set_ylabel("Abundance Difference")
    ax2.grid(True)

    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])
    fig2.colorbar(sm, ax=ax2, label="GRAVY Bin (Hydropathy)")

    fig2.tight_layout()

    plt.show()

if __name__ == "__main__":
    main()
