# Loads Precursor Abundance data from an Excel file.
# Extracts factors (Position, Load, ACN/NoACN) from sheet names.
# Computes Sum and Mean Precursor Abundance by GRAVY bins (0.05 step).
# Runs Three-Way ANOVA and Tukey HSD for ACN vs NoACN.
# Generates Boxplots for visual comparison.

import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import filedialog
import statsmodels.api as sm
import statsmodels.formula.api as smf
from statsmodels.stats.multicomp import pairwise_tukeyhsd

# === Step 1: Load Data ===
root = tk.Tk()
root.withdraw()
file_path = filedialog.askopenfilename(title="Select Precursor Abundance Excel File",
                                       filetypes=[("Excel files", "*.xlsx")])
xls = pd.ExcelFile(file_path)

# === Step 2: Extract Precursor Abundance & Conditions ===
bin_size = 0.05
gravy_bin_data = []

for sheet in xls.sheet_names:
    df_sheet = pd.read_excel(xls, sheet_name=sheet)

    if "GRAVY_without_mod" not in df_sheet.columns:
        continue

    # Parse conditions from sheet name
    parts = sheet.split("_")
    position = parts[0]  # 3.2, 3.5, 5.5
    load = parts[1]  # 50pg, 250pg
    acn_status = "ACN" if "ACN" in parts else "NoACN"

    # Aggregate precursor abundance across replicates
    abundance_columns = df_sheet.select_dtypes(include=['number']).columns
    df_sheet["Total_Abundance"] = df_sheet[abundance_columns].sum(axis=1, skipna=True)

    # Bin GRAVY scores
    df_sheet["GRAVY_Bin"] = (df_sheet["GRAVY_without_mod"] / bin_size).round() * bin_size

    # Compute Sum and Mean abundance per GRAVY bin
    bin_summary = df_sheet.groupby("GRAVY_Bin").agg(
        Sum_Abundance=("Total_Abundance", "sum"),
        Mean_Abundance=("Total_Abundance", "mean")
    ).reset_index()

    for _, row in bin_summary.iterrows():
        gravy_bin_data.append({
            "GRAVY_Bin": row["GRAVY_Bin"],
            "Position": position,
            "Load": load,
            "ACN_Status": acn_status,
            "Sum_Abundance": row["Sum_Abundance"],
            "Mean_Abundance": row["Mean_Abundance"],
        })

df_gravy_bins = pd.DataFrame(gravy_bin_data)

# === Step 3: ANOVA on Precursor Abundance ===
anova_model = smf.ols("Mean_Abundance ~ C(ACN_Status) * C(Position) * C(Load)", data=df_gravy_bins).fit()
anova_results = sm.stats.anova_lm(anova_model, typ=2)
print("\n=== ANOVA Results ===\n", anova_results)

# === Step 4: Tukey HSD for ACN vs NoACN per Position ===
for position in df_gravy_bins["Position"].unique():
    subset = df_gravy_bins[df_gravy_bins["Position"] == position]

    if subset["ACN_Status"].nunique() > 1:
        tukey = pairwise_tukeyhsd(subset["Mean_Abundance"], subset["ACN_Status"])
        print(f"\n=== Tukey HSD (Position {position}) ===\n", tukey.summary())

# === Step 5: Visualize Data ===
fig, axes = plt.subplots(1, 2, figsize=(14, 6))

# Sum Abundance Boxplot
sns.boxplot(x="Position", y="Sum_Abundance", hue="ACN_Status", data=df_gravy_bins, ax=axes[0])
axes[0].set_title("ACN vs NoACN (Sum Precursor Abundance)")
axes[0].set_xlabel("Position")
axes[0].set_ylabel("Sum Precursor Abundance")
axes[0].legend(title="ACN Status")

# Mean Abundance Boxplot
sns.boxplot(x="Position", y="Mean_Abundance", hue="ACN_Status", data=df_gravy_bins, ax=axes[1])
axes[1].set_title("ACN vs NoACN (Mean Precursor Abundance)")
axes[1].set_xlabel("Position")
axes[1].set_ylabel("Mean Precursor Abundance")
axes[1].legend(title="ACN Status")

plt.tight_layout()
plt.show()
