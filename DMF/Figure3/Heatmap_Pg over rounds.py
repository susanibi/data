import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# === Hardcoded data ===
data = {
    "Round": ["Round1"] * 4 + ["Round2"] * 4 + ["Round3"] * 4 + ["Round4"] * 4 + ["Round5"] * 4,
    "Sample": list(range(1, 21)),
    "CFL": [1.2, 1.4, 1.1, None, 2.9, 1.1, 1.0, 2.9, 0.2, 1.5, 0.3, None, 0.8, 0.2, 0.2, 0.0, 0.8, 1.0, 0.2, 0.2],
    "Sample_PG": [1141, 454, 741, 0, 1059, 0, 876, 654, 0, 369, 373, 0, None, 1, 0, 675, 2180, 330, 0, 7],
    "Residual_PG": [0, 2, 0, 118, 135, 0, 456, 708, 959, 1770, 1094, 1301, 0, 655, 784, 950, 846, 0, 0, 0]
}

df = pd.DataFrame(data)

# === Preprocessing ===
df["Well"] = df["Sample"] % 4
df["Well"] = df["Well"].replace({0: 4})

df["Round_Num"] = df["Round"].str.extract(r'(\d+)').astype(int)

# Create pivot tables for Sample and Residual PGs
sample_pg_pivot = df.pivot(index="Round_Num", columns="Well", values="Sample_PG")
residual_pg_pivot = df.pivot(index="Round_Num", columns="Well", values="Residual_PG")

# Rename columns for Sample
sample_pg_pivot.columns = [f"Well {w} (CFL)" for w in sample_pg_pivot.columns]
residual_pg_pivot.columns = [f"Well {w}" for w in residual_pg_pivot.columns]

# Shared color scale
shared_max = max(sample_pg_pivot.max().max(), residual_pg_pivot.max().max())

# === Customize your styles ===
sample_cmap = "magma"
residual_cmap = "magma"
sample_font = {"fontsize": 12, "fontweight": "bold"}
residual_font = {"fontsize": 12, "fontweight": "normal"}

# === Plot ===
fig, axes = plt.subplots(2, 1, figsize=(10, 8), sharex=True)

sns.heatmap(sample_pg_pivot, ax=axes[0], cmap=sample_cmap, annot=True, fmt=".0f",
            vmin=0, vmax=shared_max, cbar=False)
axes[0].set_title("Sample Protein Groups per Well over Rounds (CFL in parentheses)", **sample_font)
axes[0].set_ylabel("Round", **sample_font)

sns.heatmap(residual_pg_pivot, ax=axes[1], cmap=residual_cmap, annot=True, fmt=".0f",
            vmin=0, vmax=shared_max, cbar=False)
axes[1].set_title("Residual (Wash) Protein Groups per Well over Rounds", **residual_font)
axes[1].set_ylabel("Round", **residual_font)
axes[1].set_xlabel("Well", **residual_font)

plt.tight_layout()
plt.show()
