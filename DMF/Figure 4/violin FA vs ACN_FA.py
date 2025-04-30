import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# ==== COLORS ====
fa_color = "#264653"
acn_fa_color = "#457b9d"

# ==== DATA PREP ====
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
df = pd.DataFrame(data)
df["Sample_Num"] = df["File.Name"].str.extract(r'(\d+)').astype(int)
df["Type"] = df["File.Name"].apply(lambda x: "Sample" if x.startswith("S") else "Residual")
df["Sample_Type"] = df["File.Name"].apply(
    lambda x: "FA" if "FA" in x and "ACN" not in x else "ACN+FA" if "ACN+FA" in x else "Residual"
)

# ==== PLOT DATA ====
violin_data = df[df["Type"] == "Sample"].copy()
violin_data["Group"] = violin_data["Sample_Type"].replace({"FA": "Sample (FA)", "ACN+FA": "Sample (ACN+FA)"})

# ==== PLOT ====
fig, ax = plt.subplots(figsize=(8, 6))

# Violin plot with hue trick for colors
sns.violinplot(
    data=violin_data,
    x="Group",
    y="Proteins.Identified",
    hue="Group",
    palette={"Sample (FA)": fa_color, "Sample (ACN+FA)": acn_fa_color},
    inner=None,
    linewidth=1.2,
    legend=False,
    ax=ax
)

# Median diamonds
sns.pointplot(
    data=violin_data,
    x="Group",
    y="Proteins.Identified",
    dodge=False,
    color="white",
    markers="d",
    markersize=8,
    linestyle="none",
    errorbar=None,
    ax=ax
)


# Raw data points
sns.stripplot(
    data=violin_data,
    x="Group",
    y="Proteins.Identified",
    color="black",
    jitter=True,
    size=5,
    alpha=0.6,
    ax=ax
)

# Final styling
ax.set_ylabel("Protein Groups", fontsize=14)
ax.set_xlabel("")
ax.set_title("", fontsize=14, weight="bold")
ax.tick_params(axis='x', labelsize=12)
ax.tick_params(axis='y', labelsize=12)
ax.yaxis.grid(True, which='major', color='lightgrey', linestyle='-', linewidth=0.5)
ax.set_axisbelow(True)


plt.tight_layout()
plt.show()
