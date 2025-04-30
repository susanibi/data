import matplotlib.pyplot as plt

# Data from your table
cells = [
    "HEK (0.05, 0) (30)",
    "AML (0.05, 0) (45)",
    "AML,Media (0.05, 0)(30)",
    "MB (0.05, 0)(56)"
]
dropout_percentages = [23.33, 33.33, 70, 53.57]


# Define your custom colors for the bars. Change these as desired!
# HEK uses 'steelblue'; AML conditions use teal-based colors: 'teal' and 'lightseagreen';
# MB uses 'mediumpurple'.
custom_colors = ["#264653", "#748D8E", "#9AB6B6", "#66A3C2"]

plt.figure(figsize=(8, 8))

# Plot background bars for 100% level in lightgrey
background = plt.bar(cells, [100] * len(cells), color='whitesmoke', zorder=0)

# Plot the actual dropout percentage bars with custom colors on top of the background
bars = plt.bar(cells, dropout_percentages, color=custom_colors, zorder=1)

plt.ylabel('Dropout (%)', fontsize=16)
plt.xlabel('Cell (condition of F68, RG) (number inital single cell encapsulation)', fontsize=14)
plt.title('')

# Annotate each colored bar with its percentage value
for bar in bars:
    yval = bar.get_height()
    plt.text(bar.get_x() + bar.get_width() / 2, yval + 1, f'{yval:.2f}', ha='center', va='bottom', fontsize=16)

plt.xticks(rotation=45, ha='right', fontsize=14)
plt.tight_layout()
plt.show()
