import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import ttest_ind, mannwhitneyu, shapiro

# --- Data ---
data = {
    "0.05 F68": [1141, 456, 741, 118, 1194, 0, 1332, 1362, 959, 2139, 1467, 1301, 698, 656, 784, 1625, None, None, None],
    "0.02 F68 + 0.05 RG": [2459, 0, 323, 715, 1473, 2984, 0, 1481, 1657, 1923, 1310, 304, 2238, 2603, 1870, 1911, 0, 0, 1719]
}

# Convert to DataFrame
df = pd.DataFrame(data)

# Remove zeros and NaNs
df_filtered = df[(df > 0)].dropna()

# Prepare groups for stats
group1 = df_filtered["0.05 F68"]
group2 = df_filtered["0.02 F68 + 0.05 RG"]

# --- Statistical Tests ---
# Welch's t-test
t_stat, p_ttest = ttest_ind(group1, group2, equal_var=False)

# Mann-Whitney U test
u_stat, p_mwu = mannwhitneyu(group1, group2, alternative='two-sided')

# Shapiro-Wilk normality tests
shapiro1_stat, shapiro1_p = shapiro(group1)
shapiro2_stat, shapiro2_p = shapiro(group2)

# --- Plotting ---
df_melted = df_filtered.melt(var_name="Condition", value_name="Value")
colors = {
    "0.05 F68": "#264653",
    "0.02 F68 + 0.05 RG": "#a3cde3"
}

# Font sizes
title_fontsize = 20
label_fontsize = 16
tick_fontsize = 14

plt.figure(figsize=(8, 6))
sns.boxplot(data=df_melted, x="Condition", y="Value", hue="Condition", palette=colors, legend=False)
plt.title("Effect of P188 on HEK293", fontsize=title_fontsize)
plt.xlabel("", fontsize=label_fontsize)
plt.ylabel("ProteinIDs", fontsize=label_fontsize)
plt.xticks(fontsize=tick_fontsize)
plt.yticks(fontsize=tick_fontsize)
plt.grid(True, axis='y', linestyle='--', alpha=0.6)
plt.tight_layout()
plt.show()

# --- Results ---
print("### Statistical Summary (excluding 0s):\n")
print(f"Welch's t-test:       t = {t_stat:.3f},  p = {p_ttest:.3f}")
print(f"Mann–Whitney U test:  U = {u_stat:.3f},  p = {p_mwu:.3f}")
print(f"\nShapiro–Wilk Normality:")
print(f"  Group 1 (0.05 F68):           W = {shapiro1_stat:.3f},  p = {shapiro1_p:.3f}")
print(f"  Group 2 (0.02 F68 + 0.05 RG): W = {shapiro2_stat:.3f},  p = {shapiro2_p:.3f}")
