import pandas as pd
import matplotlib.pyplot as plt
from tkinter import filedialog, Tk

# === 🎨 Customize group colors here ===
GROUP_COLORS = {
    'F': 'BuGn',
    'R': 'Blues',
    'Evo': 'rosybrown',
    'Plate': 'sienna'
}


def choose_files():
    root = Tk()
    root.withdraw()
    file_paths = filedialog.askopenfilenames(
        title="Select Two Pre-summed CSV Files", filetypes=[("CSV files", "*.csv")]
    )
    return list(file_paths)


# Extract clean group name, keeping F1 ≠ F_1
def extract_sample_level(sample_name):
    core = sample_name.split('.')[0]  # removes replicate decimal
    parts = core.split('_')

    # If name like F_1 or R_2
    if len(parts) >= 2 and parts[1].isdigit():
        return f"{parts[0]}_{parts[1]}"
    return parts[0]


# Sort by type and number
def custom_sort_key(name):
    try:
        if name.startswith('Evo'):
            return (0, 0, 0)
        elif name.startswith('Plate'):
            return (1, 0, 0)
        elif name.startswith('F') and not name.startswith('F_'):
            num = ''.join(filter(str.isdigit, name))
            return (2, 0, int(num) if num else 0)  # F1, F2
        elif name.startswith('F_'):
            num = ''.join(filter(str.isdigit, name))
            return (2, 1, int(num) if num else 0)  # F_1, F_2
        elif name.startswith('R') and not name.startswith('R_'):
            num = ''.join(filter(str.isdigit, name))
            return (3, 0, int(num) if num else 0)  # R1, R2
        elif name.startswith('R_'):
            num = ''.join(filter(str.isdigit, name))
            return (3, 1, int(num) if num else 0)  # R_1, R_2
        else:
            return (4, 0, 0)
    except:
        return (5, 0, 0)



# Gradient color mapping, avoid washed-out lightest tones
def get_gradient_color_map(levels, cmap_name):
    cmap = plt.get_cmap(cmap_name)
    n = len(levels)
    return {
        level: cmap(0.3 + 0.7 * i / max(n - 1, 1))
        for i, level in enumerate(levels)
    }


def process_and_plot(file1, file2):
    df1 = pd.read_csv(file1)
    df2 = pd.read_csv(file2)

    df1.columns = [col.strip() for col in df1.columns]
    df2.columns = [col.strip() for col in df2.columns]

    combined = pd.concat([df1, df2], ignore_index=True)

    # Keep only valid samples
    combined['Sample'] = combined['Sample'].astype(str)
    combined = combined[combined['Sample'].str.match(r'^(F|R|Evo|Plate)[0-9_]*', na=False)]
    combined = combined.dropna(subset=['Sample', 'Total_Peptide_Intensity'])

    # Extract normalized sample-level group
    combined['Sample_Level'] = combined['Sample'].apply(extract_sample_level)

    # Sort by group and number
    combined['SortKey'] = combined['Sample_Level'].apply(custom_sort_key)
    combined = combined.sort_values(by='SortKey').drop(columns='SortKey')
    grouped = combined.groupby('Sample_Level', sort=False)

    # List all F* and R* levels (with and without underscores)
    all_levels = list(combined['Sample_Level'].unique())
    f_levels = [lvl for lvl in all_levels if lvl.startswith('F')]
    r_levels = [lvl for lvl in all_levels if lvl.startswith('R')]

    f_colors = get_gradient_color_map(f_levels, GROUP_COLORS['F'])
    r_colors = get_gradient_color_map(r_levels, GROUP_COLORS['R'])

    # Plotting
    x_labels = []
    intensities = []
    colors = []
    center_ticks = []
    center_labels = []

    bar_index = 0
    for name, group in grouped:
        group = group.sort_values('Sample')

        if name.startswith('F'):
            color = f_colors.get(name, 'blue')
        elif name.startswith('R'):
            color = r_colors.get(name, 'green')
        elif name.startswith('Evo'):
            color = GROUP_COLORS['Evo']
        elif name.startswith('Plate'):
            color = GROUP_COLORS['Plate']
        else:
            color = 'gray'

        colors.extend([color] * len(group))
        intensities.extend(group['Total_Peptide_Intensity'].tolist())

        # Label center of group
        start = bar_index
        end = bar_index + len(group)
        center_ticks.append((start + end - 1) / 2)
        center_labels.append(name)
        x_labels.extend([''] * len(group))
        bar_index += len(group)

        # Spacer
        intensities.append(0.0)
        x_labels.append('')
        colors.append('white')
        bar_index += 1

    x_vals = list(range(len(intensities)))

    # Plot
    plt.figure(figsize=(18, 8))
    plt.bar(x_vals, intensities, color=colors)
    plt.xticks(center_ticks, center_labels, rotation=45, ha='center', fontsize=14)
    plt.ylabel("Total Peptide Intensity", fontsize=16)
    plt.gca().yaxis.get_offset_text().set_fontsize(16)
    plt.yticks(fontsize=14)
    plt.xlabel("", fontsize=16)
    plt.title("Total peptides Abundance across all samples", fontsize=16)
    plt.tight_layout()
    plt.show()


# === Run ===
files = choose_files()
if len(files) == 2:
    process_and_plot(files[0], files[1])
else:
    print("⚠️ Please select exactly two pre-summarized CSV files.")
