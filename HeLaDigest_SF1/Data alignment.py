# This script processes two Excel files and outputs a CSV with aligned GRAVY bin data.
# It also creates a styled plot with Δ abundance, CV shading, and %PSM bars.
# the scrtip uses RAW abundance and RAW PSM output from PSM and Abundacne from RAW script

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from matplotlib.patches import Patch
import tkinter as tk
from tkinter import filedialog

# ---- File Selection (Dialog) ----
tk.Tk().withdraw()
abund_file = filedialog.askopenfilename(title="Select Output_RAW_Abundance.xlsx")
psm_file = filedialog.askopenfilename(title="Select Output_Raw_PSM_Counts_and_%PSM.xlsx")
output_path = filedialog.asksaveasfilename(defaultextension=".csv", title="Save output as")

# ---- Load and Prepare Data ----
sheet_3p2 = "3p2_50pg_NoACN"
sheet_3p5 = "3p5_50pg_NoACN"
rep_3p2 = pd.read_excel(abund_file, sheet_name=sheet_3p2).set_index("GRAVY_bin")
rep_3p5 = pd.read_excel(abund_file, sheet_name=sheet_3p5).set_index("GRAVY_bin")

# Filter replicate columns
rep_cols_3p2 = [col for col in rep_3p2.columns if sheet_3p2 in col]
rep_cols_3p5 = [col for col in rep_3p5.columns if sheet_3p5 in col]

def mean_sem_cv(df, cols):
    mean = df[cols].mean(axis=1)
    sem = df[cols].std(axis=1, ddof=1) / np.sqrt(df[cols].count(axis=1))
    cv = df[cols].std(axis=1, ddof=1) / df[cols].mean(axis=1)
    return mean, sem, cv

mean_3p2, sem_3p2, cv_3p2 = mean_sem_cv(rep_3p2, rep_cols_3p2)
mean_3p5, sem_3p5, cv_3p5 = mean_sem_cv(rep_3p5, rep_cols_3p5)

# ---- Load and combine %PSM ----
psm_3p2 = pd.read_excel(psm_file, sheet_name="3p2_50pg_NoACN_%PSM").set_index("GRAVY_bin")
psm_3p5 = pd.read_excel(psm_file, sheet_name="3p5_50pg_NoACN_%PSM").set_index("GRAVY_bin")
mean_psm = pd.concat([psm_3p2, psm_3p5]).groupby(level=0).mean().mean(axis=1)

# ---- Global GRAVY bin alignment ----
all_bins = sorted(set(mean_3p2.index)
                  .union(mean_3p5.index)
                  .union(mean_psm.index))

# ---- Build Final DataFrame ----
df = pd.DataFrame(index=all_bins)
df["3p2_50pg_NoACN_Mean"] = mean_3p2.groupby(level=0).mean().reindex(all_bins)
df["3p2_50pg_NoACN_SEM"] = sem_3p2.groupby(level=0).mean().reindex(all_bins)
df["3p5_50pg_NoACN_Mean"] = mean_3p5.groupby(level=0).mean().reindex(all_bins)
df["3p5_50pg_NoACN_SEM"] = sem_3p5.groupby(level=0).mean().reindex(all_bins)
df["Delta"] = df["3p2_50pg_NoACN_Mean"] - df["3p5_50pg_NoACN_Mean"]
df["CV_3p2"] = cv_3p2.groupby(level=0).mean().reindex(all_bins)
df["CV_3p5"] = cv_3p5.groupby(level=0).mean().reindex(all_bins)
df["Pooled_CV"] = np.sqrt(df["CV_3p2"]**2 + df["CV_3p5"]**2)
df["Mean_%PSM"] = mean_psm.groupby(level=0).mean().reindex(all_bins)

# Extract GRAVY lower bound as float
df["GRAVY_Lower"] = df.index.to_series().str.extract(r"([-+]?[0-9]*\.?[0-9]+)").astype(float)

# Force numeric conversion (safe-guard)
cols_to_force = ["GRAVY_Lower", "Delta", "Pooled_CV", "Mean_%PSM"]
df[cols_to_force] = df[cols_to_force].apply(pd.to_numeric, errors="coerce")

# Save to CSV
df.reset_index().rename(columns={"index": "GRAVY_bin"}).to_csv(output_path, index=False)
print(f"\n✅ Aligned CSV saved to: {output_path}")

# ---- Plot ----
df_plot = df.dropna(subset=["GRAVY_Lower", "Delta", "Pooled_CV", "Mean_%PSM"]).sort_values("GRAVY_Lower")

# Style settings
color_3p2 = (0.6, 0.7, 0.9, 0.25)
color_3p5 = (0.5, 0.9, 0.8, 0.25)
gray_box = "lightgrey"
norm = plt.Normalize(df_plot["GRAVY_Lower"].min(), df_plot["GRAVY_Lower"].max())
colors = cm.viridis(norm(df_plot["GRAVY_Lower"]))

# Plot
fig, ax1 = plt.subplots(figsize=(14, 7))
ax1.fill_between(df_plot["GRAVY_Lower"],
                 df_plot["Delta"] - df_plot["Pooled_CV"] * df_plot["Delta"].abs(),
                 df_plot["Delta"] + df_plot["Pooled_CV"] * df_plot["Delta"].abs(),
                 color=gray_box, alpha=0.5)

ax1.plot(df_plot["GRAVY_Lower"], df_plot["Delta"], color="black", linewidth=1)
ax1.scatter(df_plot["GRAVY_Lower"], df_plot["Delta"], c=colors, edgecolor="black", s=50)

ax1.axhline(0, color="gray", linestyle="--", linewidth=1)
ax1.set_xlabel("GRAVY bin")
ax1.set_ylabel("Δ (3.2 - 3.5)")
ax1.set_ylim(-100000, 150000)
xticks = np.linspace(df_plot["GRAVY_Lower"].min(), df_plot["GRAVY_Lower"].max(), 10)
ax1.set_xticks(xticks)
ax1.set_xticklabels([f"{x:.2f}" for x in xticks])

# Secondary axis
ax2 = ax1.twinx()
ax2.bar(df_plot["GRAVY_Lower"], df_plot["Mean_%PSM"], width=0.05, color=color_3p2, label="%PSM 3.2")
ax2.bar(df_plot["GRAVY_Lower"], df_plot["Mean_%PSM"], width=0.05, color=color_3p5, label="%PSM 3.5", bottom=0)
ax2.set_ylabel("%PSM")
ax2.set_ylim(0, 3)

# Unified legend
legend_elements = [
    Patch(facecolor=gray_box, label="CV"),
    Patch(facecolor=color_3p2, label="%PSM 3.2"),
    Patch(facecolor=color_3p5, label="%PSM 3.5")
]
ax1.legend(handles=legend_elements, loc="upper right", frameon=False)

plt.title("Effect of Position; difference vs. GRAVY")
ax1.grid(False)
ax2.grid(False)
plt.tight_layout()
plt.show()
