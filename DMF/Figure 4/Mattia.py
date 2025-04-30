import pandas as pd
import matplotlib.pyplot as plt

# ==== DATA ====
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

# ==== PARAMETERS ====
fa_color = "#264653"
acn_fa_color = "#457b9d"
residual_color = "#b0c4de"
title_fontsize = 14
label_fontsize = 14
tick_fontsize = 10
legend_fontsize = 14
bar_width = 0.35
offset = bar_width * 1.1  # controls space between sample and residual

# ==== PREP ====
df = pd.DataFrame(data)
df["Sample_Num"] = df["File.Name"].str.extract(r'(\d+)').astype(int)
df["Type"] = df["File.Name"].apply(lambda x: "Sample" if x.startswith("S") else "Residual")
df["Sample_Type"] = df["File.Name"].apply(
    lambda x: "FA" if "FA" in x and "ACN" not in x else "ACN+FA" if "ACN+FA" in x else "Residual"
)

samples_df = df[df["Type"] == "Sample"]
residuals_df = df[df["Type"] == "Residual"]

# ==== PLOT ====
fig, ax = plt.subplots(figsize=(12, 6))
ax.set_axisbelow(True)

# ==== PLOT ====
fig, ax = plt.subplots(figsize=(12, 6))
ax.set_axisbelow(True)

# Side-by-side bar placement
sample_offset = -bar_width / 2
residual_offset = bar_width / 2

# Plot samples
for idx, row in samples_df.iterrows():
    color = fa_color if row["Sample_Type"] == "FA" else acn_fa_color
    label = "Sample (FA)" if row["Sample_Type"] == "FA" else "Sample (ACN+FA)"
    show_label = (
        (label == "Sample (FA)" and idx == samples_df[samples_df["Sample_Type"] == "FA"].index[0]) or
        (label == "Sample (ACN+FA)" and idx == samples_df[samples_df["Sample_Type"] == "ACN+FA"].index[0])
    )
    ax.bar(row["Sample_Num"] + sample_offset, row["Proteins.Identified"],
           width=bar_width, color=color, label=label if show_label else "")

# Plot residuals directly next to samples
for idx, row in residuals_df.iterrows():
    show_label = (idx == residuals_df.index[0])
    ax.bar(row["Sample_Num"] + residual_offset, row["Proteins.Identified"],
           width=bar_width, color=residual_color, label="Residual" if show_label else "")

# Labels, limits, and legend
ax.set_xlabel("Sample Number", fontsize=label_fontsize)
ax.set_ylabel("Protein Groups", fontsize=label_fontsize)
ax.tick_params(axis='x', labelsize=tick_fontsize)
ax.tick_params(axis='y', labelsize=tick_fontsize)
ax.set_ylim(0, 4500)

# Force all x-ticks to display
ax.set_xticks(df["Sample_Num"].unique())
ax.set_xticklabels(df["Sample_Num"].unique(), fontsize=tick_fontsize)

# Ordered legend
handles, labels = ax.get_legend_handles_labels()
legend_order = ["Sample (FA)", "Sample (ACN+FA)", "Residual"]
ordered_handles = [handles[labels.index(name)] for name in legend_order]
ax.legend(ordered_handles, legend_order, fontsize=legend_fontsize)

# Light grey grid behind bars
ax.yaxis.grid(True, which='major', color='lightgrey', linestyle='-', linewidth=0.5)

plt.tight_layout()
plt.show()
# plt.savefig("protein_groups_plot.png", dpi=300)