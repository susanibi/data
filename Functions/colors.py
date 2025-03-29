# 🎨 Define gradient colors for Peptides (Warm Clay → Soft Taupe) and Proteins (Muted Copper)
peptide_gradient_cmap = mcolors.LinearSegmentedColormap.from_list(
    "peptide_gradient", ["#D8BFAA", "#897D75"]  # Warm Clay → Soft Taupe
)
protein_gradient_cmap = mcolors.LinearSegmentedColormap.from_list(
    "protein_gradient", ["#CA6768", "#914949"]  # Muted Copper Brown → Warm Sandstone
)


