import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from io import StringIO
import scipy.stats as stats
import itertools

# Sample data (tab-separated values)
data = """
Sample ID\tProtGroups
Control\t4599
Control\t4232
Control\t4738
Control\t4958
Control\t4671
cap\t914
cap\t0
cap\t1173
cap\t1941
cap\t1986
cap\t2361
cap\t3026
cap\t1795
pt\t258
pt\t6
pt\t0
pt\t0
pt\t2046
pt\t0
pt\t0
pt\t0
+FA, pt\t315
+FA, pt\t1710
+FA, pt\t2484
+FA, pt\t2679
+FA, pt\t2747
+FA, pt\t1750
+FA, pt\t2715
+FA, pt\t2704
+MQ, pt\t1749
+MQ, pt\t1039
+MQ, pt\t1509
+MQ, pt\t1704
"""

# Load the data into a DataFrame.
df = pd.read_csv(StringIO(data), sep="\t")

# Define a custom palette (for plotting, if needed).
custom_palette = {
    "Control": "#87ceeb",  # Soft, sky blue
    "cap": "#b0e0e6",      # r
    "pt": "#ccccff",       # Calming teal
    "+FA, pt": "#b0c4de",  # Soft pastel yellow
    "+MQ, pt": "#e6e6fa"   # Deep navy blue
}

# Create a basic boxplot for visual reference.
sns.boxplot(
    data=df,
    x="Sample ID",
    y="ProtGroups",
    hue="Sample ID",
    palette=custom_palette,
    dodge=False
)
#plt.legend([], title="")  # Remove redundant legend
plt.title("")
plt.tight_layout()
plt.show()

# --- Statistical Analysis --- #

import pandas as pd
import scipy.stats as stats
import itertools



# --- Statistical Analysis --- #

# Filter the data to include only experimental groups.
# exclude "Control" and "pt" (leaving "+FA, pt", "+MQ, pt", and "cap")
experimental_df = df[~df["Sample ID"].isin(["Control"])]

# List unique experimental groups.
groups = experimental_df["Sample ID"].unique()
print("Experimental groups compared:", groups)

# Organize data for each group.
group_data = {grp: experimental_df[experimental_df["Sample ID"] == grp]["ProtGroups"]
              for grp in groups}

# Global test: Kruskal–Wallis (non-parametric, compares overall distributions)
kw_stat, kw_p = stats.kruskal(*(group_data[grp] for grp in groups))
print("\nGlobal Kruskal-Wallis Test:")
print("H-statistic: {:.3f}, p-value: {:.3g}".format(kw_stat, kw_p))

# Pairwise comparisons using the Mann-Whitney U test.
print("\nPairwise Mann-Whitney U Tests:")
for grp1, grp2 in itertools.combinations(groups, 2):
    data1 = group_data[grp1]
    data2 = group_data[grp2]
    u_stat, p_val = stats.mannwhitneyu(data1, data2, alternative='two-sided')
    print(f"{grp1} vs {grp2}: U-statistic = {u_stat}, p-value = {p_val:.3f}")

# Consider adjusting p-values for multiple comparisons if necessary

