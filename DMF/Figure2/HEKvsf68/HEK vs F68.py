import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Data for each condition
data = {
    "0.05 P188": [1141, 456, 741, 118, 1194, 0, 1332, 1362, 959, 2139, 1467, 1301, 698, 656, 784, 1625, None, None, None],
    "0.02 P188 + 0.05 RG": [2459, 0, 323, 715, 1473, 2984, 0, 1481, 1657, 1923, 1310, 304, 2238, 2603, 1870, 1911, 0, 0, 1719]
}

# Convert to DataFrame
df = pd.DataFrame(data)

# Melt the DataFrame to long format for seaborn
df_melted = df.melt(var_name="Condition", value_name="Value")

# Define custom colors
colors = {
    "0.05 P188": "#264653",  # Deep Navy Ocean
    "0.02 P188 + 0.05 RG": "#5b9bbf"  # Blend between Soft Sky and Ocean Blue
}

# Plotting
plt.figure(figsize=(8, 6))
sns.boxplot(data=df_melted, x="Condition", y="Value", hue="Condition", palette=colors, legend=False)
plt.title("Boxplot of HEK Conditions")
plt.xlabel("Condition")
plt.ylabel("Values")
plt.grid(True, axis='y', linestyle='--', alpha=0.6)
plt.tight_layout()
plt.show()
