import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Define the data
data = """
Sample ID\tPrecursor
Control\t22395
Control\t19427
Control\t23989
Control\t24645
Control\t22883
cap\t2785
cap\t482
cap\t3462
cap\t6319
cap\t6413
cap\t8530
cap\t10471
cap\t5898
pt\t631
pt\t9
pt\t13
pt\t0
pt\t6977
pt\t137
pt\t239
pt\t13
+FA, pt\t771
+FA, pt\t5806
+FA, pt\t9086
+FA, pt\t9769
+FA, pt\t9686
+FA, pt\t4991
+FA, pt\t8653
+FA, pt\t9219
+MQ, pt\t5557
+MQ, pt\t2761
+MQ, pt\t4975
+MQ, pt\t5364
"""

# Load data into a DataFrame
from io import StringIO
df = pd.read_csv(StringIO(data), sep="\t")

# Plot
plt.figure(figsize=(10, 6))
sns.boxplot(data=df, x="Sample ID", y="Precursor")
plt.title("Precursor Distribution by Sample Type (Boxplot)")
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()
