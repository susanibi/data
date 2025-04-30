import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from io import StringIO

# Hardcoded data
csv_data = """Cell concentration (numeric),F68 (%),RG (%),Split efficiency (%)
10.0,0.02,0.0,97.27
30.0,0.05,0.15,100.0
30.0,0.05,0.0,100.0
30.0,0.05,0.0,98.44
40.0,0.02,0.05,96.88
100.0,0.01,0.0,5.0
200.0,0.01,0.0,0.0
200.0,0.02,0.01,65.23
200.0,0.04,0.0,50.0
200.0,0.03,0.0,9.38
200.0,0.02,0.0,1.56
200.0,0.01,0.0,9.38
300.0,0.0,0.0,0.0
300.0,0.0,0.0,0.0
300.0,0.0,0.0,0.0
300.0,0.0,0.05,10.94
300.0,0.01,0.05,100.0
300.0,0.01,0.0,5.0
300.0,0.05,0.0,90.63
300.0,0.05,0.0,78.13
300.0,0.05,0.0,98.44
300.0,0.05,0.0,93.36
400.0,0.01,0.0,53.13
400.0,0.02,0.01,64.0
10.0,0.04,0.01,100.0
10.0,0.05,0.0,100.0
300.0,0.05,0.0,100.0
300.0,0.05,0.0,96.89
"""
df = pd.read_csv(StringIO(csv_data))

# Compute weighted surfactant score
df["Surfactant Weighted"] = 2 * df["F68 (%)"] + 1 * df["RG (%)"]

# Create cell concentration group
df["Conc Group Refined"] = df["Cell concentration (numeric)"].apply(
    lambda x: "≤40" if x <= 40 else str(int(x))
)

# Plot with trend lines and circular dots
plot = sns.lmplot(
    data=df,
    x="Surfactant Weighted",
    y="Split efficiency (%)",
    hue="Conc Group Refined",
    palette="Set2",
    height=6,
    aspect=1.5,
    markers='o',
    scatter_kws={'s': 90, 'alpha': 0.9},
    line_kws={'linewidth': 2},
    facet_kws={'legend_out': True}
)

plt.title("Split Efficiency vs Weighted Surfactant Score\nColored by Cell Concentration (≤40 grouped)", fontsize=14)
plt.xlabel("Weighted Surfactant Score (2×F68 + 1×RG)")
plt.ylabel("Split Efficiency (%)")
plt.grid(True)
plt.tight_layout()

# Save and show
plt.savefig("split_efficiency_vs_surfactant_score.png", dpi=300)
plt.show()
