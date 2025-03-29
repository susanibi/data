import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import statsmodels.api as sm
from statsmodels.formula.api import ols
from statsmodels.stats.multicomp import pairwise_tukeyhsd
from tkinter import Tk
from tkinter.filedialog import askopenfilename

# 📂 Ask user to select the Excel file
Tk().withdraw()
file_path = askopenfilename(title="Select the Excel file", filetypes=[("Excel files", "*.xlsx")])

if not file_path:
    print("No file selected. Exiting script.")
    exit()

# Load the dataset
xls = pd.ExcelFile(file_path)
df = pd.read_excel(xls, sheet_name="Sheet1", header=1)

# Drop any empty columns
df = df.dropna(axis=1, how="all")
df = df.apply(pd.to_numeric, errors='coerce')  # Convert to numeric

# Reshape data
df_melted = df.melt(var_name="Condition", value_name="Measurement")

# Extract nanopillar height (0-10) and filter for only F_ conditions
df_melted["Nanostructure"] = df_melted["Condition"].str.extract(r'(\d+)').astype(float)
df_melted["Surface_Type"] = df_melted["Condition"].apply(lambda x: "F" if x.startswith("F_") else "R")

# Filter for only F_ conditions
df_f_only = df_melted[df_melted["Surface_Type"] == "F"].dropna()

# 🎯 Run One-Way ANOVA for Nanopillar Heights
anova_model = ols('Measurement ~ C(Nanostructure)', data=df_f_only).fit()
anova_table = sm.stats.anova_lm(anova_model, typ=2)

# 🎯 Tukey's HSD Post-Hoc Test (Only if there are multiple groups)
unique_nanostructures = df_f_only["Nanostructure"].nunique()

if unique_nanostructures > 1:
    tukey_results = pairwise_tukeyhsd(df_f_only["Measurement"], df_f_only["Nanostructure"])

    # 🎯 Convert Tukey results into a DataFrame
    tukey_summary = pd.DataFrame(data=tukey_results._results_table.data[1:], columns=tukey_results._results_table.data[0])

    # Rename columns for clarity
    tukey_summary = tukey_summary.rename(columns={
        "group1": "Nanostructure 1",
        "group2": "Nanostructure 2",
        "meandiff": "Mean Difference",
        "p-adj": "p-value",
        "lower": "Lower CI",
        "upper": "Upper CI",
        "reject": "Significant"
    })

    # Convert p-values into a pivot table for heatmap
    tukey_pivot = tukey_summary.pivot(index="Nanostructure 1", columns="Nanostructure 2", values="p-value")

    # Set upper triangle to NaN to avoid duplicate values
    for i in range(len(tukey_pivot)):
        for j in range(i+1):
            tukey_pivot.iloc[i, j] = np.nan

    # 🎯 Create combined significance markers (p-value + stars)
    def combined_marker_revised(p):
        if p < 0.001:
            return f"{p:.3f}\n(***)"
        elif p < 0.01:
            return f"{p:.3f}\n(**)"
        elif p < 0.05:
            return f"{p:.3f}\n(*)"
        else:
            return f"{p:.3f}"  # Show raw p-value if not significant

    tukey_pivot_combined = tukey_pivot.applymap(combined_marker_revised)

    # 🎨 Define a nature-inspired green palette (darker = more significant)
    green_palette_reversed = sns.color_palette(["#254D32", "#3A5F0B", "#6B8E23", "#A8D5BA", "#E3F2E1"])

    # 🎨 Plot heatmap with reversed green tones (darker = higher significance)
    plt.figure(figsize=(8, 6))
    sns.heatmap(tukey_pivot, annot=tukey_pivot_combined, cmap=green_palette_reversed, cbar=True, linewidths=0.5, fmt="")

    plt.title("Pairwise Tukey HSD Results for Nanostructure Heights (F Surface)")
    plt.xlabel("Nanostructure 2")
    plt.ylabel("Nanostructure 1")
    plt.show()

    # 🎯 Save Tukey Results
    tukey_results_path = os.path.join(os.path.dirname(file_path), "tukey_f_results.xlsx")
    tukey_summary.to_excel(tukey_results_path, index=False)
    print(f"📈 Tukey HSD Results saved: {tukey_results_path}")

else:
    print("⚠️ Tukey's HSD Test could not be performed: Not enough unique nanostructure levels.")

# 🎯 Save ANOVA Results
anova_results_path = os.path.join(os.path.dirname(file_path), "anova_f_results.xlsx")
anova_table.to_excel(anova_results_path)
print(f"📄 ANOVA Results saved: {anova_results_path}")
