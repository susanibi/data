import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Updated sample data with two measurements for ACX
data = {
    "label": [
        "ACX\n(n=2)", "MQ\n(n=1)", "20 TFE\n0.15 RG\n(n=4)",
        "20 TFE\n0.2 RG\n(n=2)", "14TFE\n0.15 RG (MQ),\n53 C\n(n=2)",
        "14TFE\n0.15 RG \n53 C\n(n=4)"
    ],
    "exp 1": [100, 100, 46.875, 96.875, 100, 100],
    "exp 2": [93.75, np.nan, 89.0625, 100, 100, 100],
    "exp 3": [np.nan, np.nan, 28.125, np.nan, 84.375, np.nan],
    "exp 4": [np.nan, np.nan, 18.75, np.nan, 81.25, np.nan],
    "exp 5": [np.nan, np.nan, 0, np.nan, np.nan, np.nan]
}

df = pd.DataFrame(data)

# Reshape data to long format and drop NaN values
df_long = df.melt(id_vars='label', value_name='split_rate').dropna()

# Compute summary statistics (mean and standard deviation)
summary = df_long.groupby('label').agg(
    mean_split_rate=('split_rate', 'mean'),
    std_split_rate=('split_rate', 'std')
).reset_index()

# For groups with a single observation, replace NaN std with 0
summary['std_split_rate'] = summary['std_split_rate'].fillna(0)

# Define a custom order for the bars
custom_order = [
    "MQ\n(n=1)",
    "ACX\n(n=2)",
    "20 TFE\n0.15 RG\n(n=4)",
    "20 TFE\n0.2 RG\n(n=2)",
    "14TFE\n0.15 RG (MQ),\n53 C\n(n=2)",
    "14TFE\n0.15 RG \n53 C\n(n=4)"
]
summary['label'] = pd.Categorical(summary['label'], categories=custom_order, ordered=True)
summary = summary.sort_values('label')

# ---------------------------
# Define explicit colors for each group:
# ---------------------------
colors = {
    "MQ": "#B4DCEC",        # A distinct, lighter greyish-teal for MQ
    "ACX": "#5C797D",       # A different for ACX
    "20 TFE": "#589EA8",    # Slightly darker version for 20 TFE
    "14TFE": "#94CACF"      # Lighter tone for 14TFE
}

# Function to choose the color based on the label
def assign_color(label):
    label_str = str(label)
    if label_str.startswith("MQ"):
        return colors["MQ"]
    elif label_str.startswith("ACX"):
        return colors["ACX"]
    elif label_str.startswith("20 TFE"):
        return colors["20 TFE"]
    elif label_str.startswith("14TFE"):
        return colors["14TFE"]
    else:
        return "#CCCCCC"  # fallback color

# Create a list of colors for the bars in order
bar_colors = summary['label'].astype(str).apply(assign_color).tolist()

# Plotting the bar chart with explicit colors and a reduced bar width
plt.figure(figsize=(10, 6))
bars = plt.bar(
    summary['label'],
    summary['mean_split_rate'],
    width=0.5,  # Reduced width (default is often around 0.8)
    yerr=summary['std_split_rate'],
    color=bar_colors,
    capsize=5,
    alpha=0.6,
    edgecolor='black'
)

# Optional: Add a background shading up to 100%
for bar in bars:
    plt.gca().add_patch(
        plt.Rectangle(
            (bar.get_x(), 0),
            bar.get_width(),  # This automatically adjusts to the new width
            100,
            color='gray', alpha=0.1, zorder=0
        )
    )

plt.title("", fontsize=16)
plt.ylabel("% Split Rate", fontsize=14)
plt.xticks(rotation=0, ha='center', fontsize=12)
plt.yticks(fontsize=12)

plt.tight_layout()
plt.savefig("high_res_plot.png", dpi=300, bbox_inches='tight')
plt.show()
