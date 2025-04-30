import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import mannwhitneyu

# ==== COLORS ====
fa_color = "#264653"
acn_fa_color = "#457b9d"
eclipse_color = "#b0c4de"  # using this color for Eclipse

# ==== ASTRAL Data: keep only sample rows (file names starting with "S") ====
data = {
    "File.Name": [
        "S1 FA", "w1", "S2 FA", "w2", "S3 FA", "w3", "S4 FA", "w4", "S5 FA", "w5",
        "S6 ACN+FA", "w6", "S7 ACN+FA", "w7", "S8 ACN+FA", "w8", "S9 ACN+FA", "w9",
        "S10 ACN+FA", "w10", "S11 ACN+FA", "w11", "S12 ACN+FA", "w12", "S13 ACN+FA", "w13"
    ],
    "Precursors.Identified": [
        13308, 374, 9929, 206, 12405, 346, 11806, 657, 11891, 137,
        10742, 150, 13310, 41, 16989, 212, 16203, 1450,
        12401, 113, 14610, 184, 17684, 103, 19251, 804
    ],
    "Proteins.Identified": [
        3488, 176, 3029, 0, 3499, 143, 3264, 269, 3036, 0,
        2802, 0, 3186, 0, 3747, 0, 3780, 557,
        3133, 0, 3457, 0, 3883, 0, 4004, 238
    ]
}
df_data = pd.DataFrame(data)
# Only keep rows whose File.Name starts with "S" (samples, not residual "w" rows)
df_data = df_data[df_data["File.Name"].str.startswith("S")].copy()
df_data["Type"] = "Astral"

# ==== Eclipse Data: new dataset with 13 rows ====
new_data = {
    "File.Name": [
        "E1 Eclipse", "E2 Eclipse", "E3 Eclipse", "E4 Eclipse", "E5 Eclipse",
        "E6 Eclipse", "E7 Eclipse", "E8 Eclipse", "E9 Eclipse",
        "E10 Eclipse", "E11 Eclipse", "E12 Eclipse", "E13 Eclipse"
    ],
    "Precursors.Identified": [
        14000, 10000, 12500, 11900, 10800, 13400, 17000, 16300, 12500,
        14700, 17700, 19300, 15000
    ],
    "Proteins.Identified": [
        1657, 1923, 1625, 304, 959, 656, 1467, 1301, 2238,
        2603, 1870, 784, None  # If missing, use None / NaN
    ]
}
df_new_data = pd.DataFrame(new_data)
# Reorder columns if necessary to match df_data, then assign Type as Eclipse
df_new_data = df_new_data.reindex(columns=df_data.columns)
df_new_data["Type"] = "Eclipse"

# ==== Combine the datasets ====
df = pd.concat([df_data, df_new_data], ignore_index=True)

# Set Sample_Type: For Astral, use "ACN+FA" if the file name contains that substring, else "FA".
# For Eclipse, force Sample_Type to "FA" (per the table you provided).
df["Sample_Type"] = df["File.Name"].apply(
    lambda x: "ACN+FA" if ("ACN+FA" in x) else "FA"
)
df.loc[df["Type"] == "Eclipse", "Sample_Type"] = "FA"

# ==== Prepare Groups for Analysis ====
# Astral group is split into FA and ACN+FA.
astral_fa = df[(df["Type"] == "Astral") & (df["Sample_Type"] == "FA")]["Proteins.Identified"]
astral_acn_fa = df[(df["Type"] == "Astral") & (df["Sample_Type"] == "ACN+FA")]["Proteins.Identified"]
# Eclipse group: take Proteins.Identified values, dropping missing values.
eclipse_vals = df[df["Type"] == "Eclipse"]["Proteins.Identified"].dropna()

# ==== Perform Statistics ====
stat_astral_acn_fa, p_astral_acn_fa = mannwhitneyu(astral_fa, astral_acn_fa, alternative='two-sided')
stat_astral_eclipse, p_astral_eclipse = mannwhitneyu(astral_fa, eclipse_vals, alternative='two-sided')
stat_acn_fa_eclipse, p_acn_fa_eclipse = mannwhitneyu(astral_acn_fa, eclipse_vals, alternative='two-sided')

print(f"Mann-Whitney U test Astral FA vs Astral ACN+FA: U={stat_astral_acn_fa}, p={p_astral_acn_fa:.4f}")
print(f"Mann-Whitney U test Astral FA vs Eclipse: U={stat_astral_eclipse}, p={p_astral_eclipse:.4f}")
print(f"Mann-Whitney U test Astral ACN+FA vs Eclipse: U={stat_acn_fa_eclipse}, p={p_acn_fa_eclipse:.4f}")

# ==== Box Plot ====
fig, ax = plt.subplots(figsize=(8, 6))

# Group data in the desired order: Astral (FA), Astral (ACN+FA), Eclipse.
grouped_data = [astral_fa, astral_acn_fa, eclipse_vals]

bp = ax.boxplot(
    grouped_data,
    patch_artist=True,
    widths=0.3,
    positions=[1, 1.5, 2],
    tick_labels=["Astral (FA)", "Astral (ACN+FA)", "Eclipse"],
    boxprops=dict(color="black"),
    medianprops=dict(color="grey", linewidth=2),
    whiskerprops=dict(color="black"),
    capprops=dict(color="black"),
    flierprops=dict(marker='o', markersize=5, markerfacecolor='gray', markeredgecolor='black')
)

# Apply custom fill colors
colors = [fa_color, acn_fa_color, eclipse_color]
for patch, color in zip(bp['boxes'], colors):
    patch.set_facecolor(color)

ax.set_ylabel("Protein Groups", fontsize=14)
ax.set_title("", fontsize=14, weight='bold')
ax.tick_params(axis='x', labelsize=14)
ax.tick_params(axis='y', labelsize=14)
ax.yaxis.grid(True, which='major', color='lightgrey', linestyle='-', linewidth=0.5)

plt.tight_layout()
plt.show()
