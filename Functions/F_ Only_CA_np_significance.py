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
df_f_only = df_melted[df_melted["Surface_Type"] == "F"]

# 🎯 Run One-Way ANOVA for Nanopillar Heights within F_
anova_f_model = ols('Measurement ~ C(Nanostructure)', data=df_f_only).fit()
anova_f_table = sm.stats.anova_lm(anova_f_model, typ=2)

# 🎨 Visualizing p-values with a Heatmap
anova_f_pvals = anova_f_table["PR(>F)"].to_frame().rename(columns={"PR(>F)": "p-value"})
anova_f_pvals.index = anova_f_table.index

plt.figure(figsize=(4, 2))
sns.heatmap(anova_f_pvals, annot=True, cmap="coolwarm", cbar=True, linewidths=0.5, fmt=".3f")
plt.title("One-Way ANOVA (F_ Nanopillar Heights)")
plt.show()

# 🎯 Tukey's HSD Post-Hoc Test (To see which heights differ)
unique_nanostructures = df_f_only["Nanostructure"].nunique()

if unique_nanostructures > 1:  # Ensure Tukey's test has at least two groups
    tukey_results = pairwise_tukeyhsd(df_f_only["Measurement"], df_f_only["Nanostructure"])

    # 🎨 Visualization of Tukey's HSD Results
    fig, ax = plt.subplots(figsize=(8, 5))
    tukey_results.plot_simultaneous(ax=ax)
    plt.title("Tukey HSD for F_ Nanopillar Heights")
    plt.xlabel("Measurement")
    plt.show()

    # 🎯 Save Tukey Results
    tukey_results_path = os.path.join(os.path.dirname(file_path), "tukey_f_results.xlsx")
    pd.DataFrame(data=tukey_results._results_table.data[1:], columns=tukey_results._results_table.data[0]).to_excel(tukey_results_path, index=False)
    print(f"📈 Tukey HSD Results saved: {tukey_results_path}")

else:
    print("⚠️ Tukey's HSD Test could not be performed: Not enough unique nanostructure levels.")

# 🎯 Save ANOVA Results
anova_f_results_path = os.path.join(os.path.dirname(file_path), "anova_f_results.xlsx")
anova_f_table.to_excel(anova_f_results_path)
print(f"📄 ANOVA Results saved: {anova_f_results_path}")
