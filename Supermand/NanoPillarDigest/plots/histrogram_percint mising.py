import pandas as pd
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import filedialog
import numpy as np
from scipy.stats import gaussian_kde, ks_2samp

# ====== USER SETTINGS ======
p1_color = 'purple'
p2_color = 'orange'
bins_number = 20
alpha_value = 0.3  # Lighter histograms for KDE overlay
# ===========================

def load_and_compute_custom_missing(path, group_type):
    df = pd.read_csv(path)

    if group_type == 'P2':
        prefixes = [f"{prefix}_{i}" for prefix in ['F', 'R'] for i in range(1, 6)]
        extras = ['F1_', 'F2_', 'R1_', 'R2_']
        cols = [c for c in df.columns if any(c.startswith(p) for p in prefixes + extras)]
    elif group_type == 'P1':
        prefixes = [f"{prefix}_{i}" for prefix in ['F', 'R'] for i in range(6, 11)]
        cols = [c for c in df.columns if any(c.startswith(p) for p in prefixes)]
    else:
        cols = []

    missing_pct = (df[cols] == 0).sum() / df.shape[0] * 100
    return missing_pct

def print_stats(name, data):
    print(f"\n{name} Missing Peptides Stats:")
    print(f"  Mean   : {data.mean():.2f}")
    print(f"  Median : {data.median():.2f}")
    print(f"  Std Dev: {data.std():.2f}")
    print(f"  Min    : {data.min():.2f}")
    print(f"  Max    : {data.max():.2f}")

def run_ks_test(data1, data2):
    stat, p_value = ks_2samp(data1, data2)
    print("\nKolmogorov-Smirnov Test (P1 vs P2):")
    print(f"  KS Statistic = {stat:.3f}")
    print(f"  p-value      = {p_value:.4f}")
    if p_value < 0.05:
        print("  ➜ The distributions are significantly different (p < 0.05).")
    else:
        print("  ➜ No significant difference between distributions.")

def plot_kde_with_hist(missing_p1, missing_p2):
    kde_p1 = gaussian_kde(missing_p1)
    kde_p2 = gaussian_kde(missing_p2)

    x_min = min(missing_p1.min(), missing_p2.min())
    x_max = max(missing_p1.max(), missing_p2.max())
    x_vals = np.linspace(x_min, x_max, 500)

    plt.figure(figsize=(10, 6))

    plt.hist(missing_p1, bins=bins_number, alpha=alpha_value, density=True, color=p1_color, label='P1 Histogram')
    plt.hist(missing_p2, bins=bins_number, alpha=alpha_value, density=True, color=p2_color, label='P2 Histogram')

    plt.plot(x_vals, kde_p1(x_vals), color=p1_color, linewidth=2, label='P1 KDE')
    plt.plot(x_vals, kde_p2(x_vals), color=p2_color, linewidth=2, label='P2 KDE')

    plt.xlabel('% Missing Peptides')
    plt.ylabel('Density')
    plt.title('Missing Peptides Distribution with KDE Overlay')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

def main():
    root = tk.Tk()
    root.withdraw()

    print("Select P2 dataset...")
    path_p2 = filedialog.askopenfilename(title="Select P2 dataset", filetypes=[("CSV files","*.csv")])
    if not path_p2:
        print("No file selected for P2. Exiting.")
        return

    print("Select P1 dataset...")
    path_p1 = filedialog.askopenfilename(title="Select P1 dataset", filetypes=[("CSV files","*.csv")])
    if not path_p1:
        print("No file selected for P1. Exiting.")
        return

    missing_p2 = load_and_compute_custom_missing(path_p2, 'P2')
    missing_p1 = load_and_compute_custom_missing(path_p1, 'P1')

    # Output statistics
    print_stats("P2", missing_p2)
    print_stats("P1", missing_p1)

    # Run KS test
    run_ks_test(missing_p1, missing_p2)

    # Plot with KDE
    plot_kde_with_hist(missing_p1, missing_p2)

if __name__ == "__main__":
    main()
