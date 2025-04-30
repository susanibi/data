import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# Provided data
data = {
    "H2O": {"TA_pillar": [57.0, 36.0, 32.0], "TA_smooth": [90.0, 90.0]},
    "TEAB": {"TA_pillar": [42.0, 52.0, 47.0, 46.0], "TA_smooth": [74.0]},
    "50pg": {"TA_pillar": [43.0, 90.0], "TA_smooth": [90.0]},
    "200pg": {"TA_pillar": [77.0, 90.0, 74.0], "TA_smooth": [74.0]},
}

# Custom muted color palette
custom_colors = {
    "H2O_pillar": "#a8ddb5",  # soft green
    "H2O_smooth": "#006d2c",  # forest green

    "TEAB_pillar": "#b3cde3", # light blue
    "TEAB_smooth": "#08519c", # navy blue

    "50pg_pillar": "#c994c7", # soft violet
    "50pg_smooth": "#6a51a3", # deep violet

    "200pg_pillar": "#d0c4df", # muted lilac-gray
    "200pg_smooth": "#726a95", # muted dark lavender-gray
}

# Create figure and axis
fig, ax = plt.subplots(figsize=(8, 5))

# For building custom legend entries
legend_elements = []

# Plot the data
for key in data:
    for surface in data[key]:
        color_key = f"{key}_{surface.split('_')[1]}"
        label_surface = surface.replace('TA_', '').capitalize()
        scatter = ax.scatter(
            [key] * len(data[key][surface]),
            data[key][surface],
            color=custom_colors[color_key],
            edgecolor='none',  # No border on normal points
            alpha=0.9,
            s=80,
            label=f"{key} - {label_surface}"
        )
        # Save legend handles manually
        legend_elements.append(mpatches.Patch(color=custom_colors[color_key], label=f"{key} - {label_surface}"))

# Highlight 74 values only with thin black ring
for key in data:
    for surface in data[key]:
        for value in data[key][surface]:
            if value == 74.0:
                ax.scatter(
                    key,
                    value,
                    facecolor='none',
                    edgecolor='black',
                    linewidth=1.2,
                    s=70
                )

# Insert "blank" elements into the legend for visual spacing
spacer = mpatches.Patch(color='none', label='')

# Custom legend order with spacers
custom_legend = [
    legend_elements[0], legend_elements[1], spacer,  # H2O pillar + smooth
    legend_elements[2], legend_elements[3], spacer,  # TEAB pillar + smooth
    legend_elements[4], legend_elements[5], spacer,  # 50pg pillar + smooth
    legend_elements[6], legend_elements[7],          # 200pg pillar + smooth
]

# Set labels and title
ax.set_xlabel("", fontsize=14)
ax.set_ylabel("Angle degrees", fontsize=14)
ax.set_title("Tilt angles", fontsize=14, weight='bold')

# Customize ticks
ax.tick_params(axis='both', which='major', labelsize=14)

# Remove grid
ax.grid(False)

# Add custom legend with spacing
ax.legend(handles=custom_legend, loc='center left', bbox_to_anchor=(1, 0.5), fontsize=12, frameon=False)

# Tight layout
plt.tight_layout()

# Show the plot
plt.show()
