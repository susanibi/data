import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import statsmodels.api as sm
from statsmodels.formula.api import ols
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

# Reshape data for Two-Way ANOVA
df_melted = df.melt(var_name="Condition", value_name="Measurement")

# Extract the numerical part of F_ and R_ conditions (nanostructure level)
df_melted["Nanostructure"] = df_melted["Condition"].str.extract(r'(\d+)').astype(float)
df_melted["Surface_Type"] = df_melted["Condition"].apply(lambda x: "F" if x.startswith("F_") else "R")

# 🎯 Fit Two-Way ANOVA model
anova_model = ols('Measurement ~ C(Surface_Type) + C(Nanostructure) + C(Surface_Type):C(Nanostructure)', data=df_melted).fit()
anova_table = sm.stats.anova_lm(anova_model, typ=2)

# 🎨 Visualizing p-values with a Heatmap
anova_pvals = anova_table["PR(>F)"].to_frame().rename(columns={"PR(>F)": "p-value"})
anova_pvals.index = anova_table.index  # Ensuring correct labels

# 🔥 Plot heatmap of p-values
plt.figure(figsize=(6, 3))
sns.heatmap(anova_pvals, annot=True, cmap="coolwarm", cbar=True, linewidths=0.5, fmt=".3f")
plt.title("Two-Way ANOVA p-Values Heatmap")
plt.xticks(rotation=45)
plt.tight_layout()

# Save heatmap as PNG
heatmap_path = os.path.join(os.path.dirname(file_path), "anova_pvalues_heatmap.png")
plt.savefig(heatmap_path, dpi=300, bbox_inches="tight")

# Show the heatmap
plt.show()

# 🎯 Save ANOVA results to Excel
anova_results_path = os.path.join(os.path.dirname(file_path), "anova_results.xlsx")
anova_table.to_excel(anova_results_path)

# 🎉 Print Output File Paths
print("\n✅ All files have been saved in the same folder as your selected Excel file:")
print(f"📊 ANOVA p-Value Heatmap: {heatmap_path}")
print(f"📈 ANOVA Results (Excel): {anova_results_path}")
